#!/usr/bin/env bash
# Run from the project root with the existing venv activated.
# Default: build and validate a temporary copy; no source files changed.
set -euo pipefail
exec python - "$@" <<'PY'
import ast
import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

root = Path.cwd().resolve()
app = root / 'backend/app'
mode = sys.argv[1] if len(sys.argv) > 1 else '--check'
backups = root / '.healthlink-refactor-backups'

def stop(message):
    raise SystemExit('STOP: ' + message)

if sys.version_info < (3, 10):
    stop('Activate your existing Python 3.12 virtual environment first.')
if mode not in ('--check', '--apply', '--restore'):
    stop('Usage: bash restructure_healthlink.sh [--check | --apply | --restore BACKUP_PATH]')
if not app.is_dir():
    stop('Run from the project root containing backend/app.')

if mode == '--restore':
    if len(sys.argv) != 3:
        stop('Provide the backup path printed by --apply.')
    backup = Path(sys.argv[2]).resolve()
    if backup.parent != backups.resolve() or not (backup / 'REFRACTOR_BACKUP').is_file():
        stop('Not a backup created by this script in this project.')
    if not (backup / 'app').is_dir():
        stop('Backup app directory missing.')
    saved = backups / ('before-restore-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    saved.mkdir(parents=True)
    app.rename(saved / 'app')
    try:
        shutil.copytree(backup / 'app', app)
    except BaseException:
        if app.exists():
            shutil.rmtree(app)
        (saved / 'app').rename(app)
        raise
    print('Restored original backend/app. Pre-restore code retained at:', saved)
    raise SystemExit(0)

if (app / 'core/config.py').exists() or (app / 'agent').exists():
    stop('Already structured (or a target folder exists). Nothing changed.')
if any(p.is_symlink() for p in app.rglob('*')):
    stop('Symlinks found in app; review manually before restructuring.')

moves = {
    'database': 'db.database', 'models': 'db.models',
    'init_db': 'db.init_db', 'seed_doctors': 'db.seed_doctors',
    'doctor_routes': 'routes.doctor_routes',
    'conversation_routes': 'routes.conversation_routes',
    'appointment_routes': 'routes.appointment_routes',
    'chat_routes': 'routes.chat_routes',
    'doctor_service': 'services.doctor_service',
    'conversation_service': 'services.conversation_service',
    'slot_service': 'services.slot_service',
    'appointment_service': 'services.appointment_service',
    'scheduling': 'services.scheduling',
    'agent': 'agent.graph', 'llm_client': 'agent.llm_client',
    'agent_tools': 'tools.executor',
}
required = ['main', 'database', 'models', 'agent', 'agent_tools', 'llm_client',
            'chat_routes', 'conversation_routes', 'doctor_routes',
            'doctor_service', 'conversation_service']
for name in required:
    if not (app / (name + '.py')).is_file():
        stop('Expected flat-layout file missing: ' + name + '.py')

sources = {p.name: p.read_text() for p in app.glob('*.py')}
for name, source in sources.items():
    tree = ast.parse(source, filename=name)
    if any(isinstance(n, ast.ImportFrom) and n.level for n in ast.walk(tree)):
        stop(name + ': relative imports require manual review.')
    if any(isinstance(n, ast.Import) and any(a.name.startswith('app.') for a in n.names)
           for n in ast.walk(tree)):
        stop(name + ': use of import app.* requires manual review.')

# Byte offsets preserve all unrelated code and comments, including non-ASCII prompts.
def edit_nodes(source, edits):
    data = source.encode()
    lines = data.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    spans = []
    for node, replacement in edits:
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        spans.append((start, end, replacement.encode()))
    for start, end, replacement in sorted(spans, reverse=True):
        data = data[:start] + replacement + data[end:]
    return data.decode()

def extract_assignment(source, name):
    matches = [n for n in ast.parse(source).body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    if len(matches) != 1:
        stop('Expected one assignment for ' + name)
    return matches[0]

# Preserve the exact current agent prompt, including local fixes.
agent_source = sources['agent.py']
prompt_node = extract_assignment(agent_source, 'AGENT_PROMPT')
try:
    prompt = ast.literal_eval(prompt_node.value)
except Exception:
    stop('AGENT_PROMPT must be a literal string; no changes applied.')
if not isinstance(prompt, str):
    stop('AGENT_PROMPT must be a string.')
sources['agent.py'] = edit_nodes(agent_source, [(prompt_node,
    'from app.prompts import load_healthlink_prompt\nAGENT_PROMPT = load_healthlink_prompt()')])

# Split tool schemas from their executable implementations.
tool_source = sources['agent_tools.py']
tools_node = extract_assignment(tool_source, 'TOOLS')
try:
    ast.literal_eval(tools_node.value)
except Exception:
    stop('TOOLS must be a literal list for this migration.')
definitions = ast.get_source_segment(tool_source, tools_node) + '\n'
sources['agent_tools.py'] = edit_nodes(tool_source, [(tools_node,
    'from app.tools.definitions import TOOLS')])

# Centralize existing os.getenv expressions, preserving their current defaults.
config_values = {}
for filename in ('database.py', 'llm_client.py'):
    source = sources[filename]
    edits = []
    for node in ast.walk(ast.parse(source)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == 'os' and node.func.attr == 'getenv'):
            if not node.args or not isinstance(node.args[0], ast.Constant):
                stop(filename + ': dynamic getenv expression requires review.')
            key = node.args[0].value
            if not isinstance(key, str) or not key.isidentifier():
                stop('Unsupported environment key.')
            expression = ast.get_source_segment(source, node)
            if key in config_values and config_values[key] != expression:
                stop('Different defaults for environment key: ' + key)
            config_values[key] = expression
            edits.append((node, 'config.' + key))
    source = edit_nodes(source, edits)
    # Only remove known root calculation and dotenv calls; fail on unfamiliar paths.
    root_line = 'PROJECT_ROOT = Path(__file__).resolve().parents[2]'
    if root_line not in source or 'load_dotenv(PROJECT_ROOT / ".env")' not in source:
        stop(filename + ': unfamiliar .env/root loading code; nothing changed.')
    source = source.replace(root_line, 'from app.core.config import PROJECT_ROOT')
    source = source.replace('load_dotenv(PROJECT_ROOT / ".env")', 'from app.core import config')
    sources[filename] = source

# Move existing operational constants without changing their values.
for filename in ('agent.py', 'llm_client.py'):
    source = sources[filename]
    edits = []
    for node in ast.walk(ast.parse(source)):
        if (filename == 'agent.py' and isinstance(node, ast.Compare)
                and isinstance(node.left, ast.Subscript)
                and isinstance(node.left.slice, ast.Constant)
                and node.left.slice.value == 'model_calls'
                and len(node.comparators) == 1
                and isinstance(node.comparators[0], ast.Constant)
                and isinstance(node.comparators[0].value, int)):
            value = node.comparators[0]
            config_values['MAX_TOOL_ROUNDS'] = repr(value.value)
            edits.append((value, 'config.MAX_TOOL_ROUNDS'))
        if (filename == 'llm_client.py' and isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name) and node.func.id == 'AsyncOpenAI'):
            for keyword in node.keywords:
                key = {'timeout': 'LLM_TIMEOUT_SECONDS', 'max_retries': 'LLM_MAX_RETRIES'}.get(keyword.arg)
                if key and isinstance(keyword.value, ast.Constant):
                    config_values[key] = repr(keyword.value.value)
                    edits.append((keyword.value, 'config.' + key))
    if edits:
        source = edit_nodes(source, edits)
        if filename == 'agent.py':
            # Insert after imports to preserve any future-import placement.
            anchor = next(n for n in ast.parse(source).body if isinstance(n, ast.ImportFrom))
            segment = ast.get_source_segment(source, anchor)
            source = edit_nodes(source, [(anchor, segment + '\nfrom app.core import config')])
        sources[filename] = source

config_text = '''"""Environment settings. Secrets stay in .env or deployment environment."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Override is useful for isolated verification; normally inferred from this file.
PROJECT_ROOT = Path(os.environ.get(
    "HEALTHLINK_PROJECT_ROOT", str(Path(__file__).resolve().parents[3])
)).resolve()
load_dotenv(PROJECT_ROOT / ".env")

'''
config_text += '\n'.join(f'{key} = {value}' for key, value in config_values.items()) + '\n'

# Move API models, retaining the legacy chat route for compatibility.
def extract_classes(filename, names, module):
    source = sources[filename]
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in names]
    if not nodes:
        stop('No expected schemas in ' + filename)
    imports = []
    for n in tree.body:
        if isinstance(n, ast.ImportFrom) and n.module in ('pydantic', 'uuid', 'datetime', 'typing'):
            imports.append(ast.get_source_segment(source, n))
    schema = '\n'.join(imports) + '\n\n'
    schema += '\n\n'.join(ast.get_source_segment(source, n) for n in nodes) + '\n'
    edits = [(n, '') for n in nodes]
    edits[0] = (nodes[0], f'from {module} import ' + ', '.join(n.name for n in nodes))
    sources[filename] = edit_nodes(source, edits)
    return schema

chat_schema = extract_classes('chat_routes.py',
    {'ChatRequest', 'ChatResponse', 'BookingProposal'}, 'app.schemas.chat')
appointment_schema = None
if 'appointment_routes.py' in sources:
    appointment_schema = extract_classes('appointment_routes.py',
        {'AppointmentRequest'}, 'app.schemas.appointment')

# Rewrite absolute from-imports without touching prompt text or string literals.
def rewrite_imports(source):
    edits = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and node.module:
            old = node.module
            if old.startswith('app.') and old[4:] in moves:
                new = 'app.' + moves[old[4:]]
                if old == 'app.chat_routes' and all(
                    a.name in {'ChatRequest', 'ChatResponse', 'BookingProposal'} for a in node.names
                ):
                    new = 'app.schemas.chat'
                segment = ast.get_source_segment(source, node)
                edits.append((node, segment.replace('from ' + old, 'from ' + new, 1)))
    return edit_nodes(source, edits)

with tempfile.TemporaryDirectory(prefix='healthlink-refactor-') as temp:
    staged = Path(temp) / 'app'
    shutil.copytree(app, staged, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for folder in ('core', 'db', 'routes', 'schemas', 'services', 'agent', 'tools', 'prompts'):
        target = staged / folder
        if target.exists():
            stop('Target folder already exists: ' + folder)
        target.mkdir()
        (target / '__init__.py').write_text('')
    for filename, source in sources.items():
        name = filename[:-3]
        if name in moves:
            target = staged / (moves[name].replace('.', '/') + '.py')
            target.write_text(rewrite_imports(source))
            old = staged / filename
            if name == 'agent':
                old.unlink()
            else:
                shim = '# Compatibility import; edit the implementation in its new folder.\n'
                shim += f'from app.{moves[name]} import *\n'
                if name in ('init_db', 'seed_doctors'):
                    shim += '\nif __name__ == "__main__":\n    main()\n'
                old.write_text(shim)
        else:
            (staged / filename).write_text(rewrite_imports(source))
    (staged / 'agent/__init__.py').write_text('from app.agent.graph import build_agent, AgentState\n')
    (staged / 'core/config.py').write_text(config_text)
    (staged / 'schemas/chat.py').write_text(chat_schema)
    if appointment_schema:
        (staged / 'schemas/appointment.py').write_text(appointment_schema)
    (staged / 'tools/definitions.py').write_text(definitions)
    (staged / 'prompts/healthlink.txt').write_text(prompt)
    (staged / 'prompts/__init__.py').write_text(
        'from pathlib import Path\n\n'
        'def load_healthlink_prompt():\n'
        '    return Path(__file__).with_name("healthlink.txt").read_text(encoding="utf-8")\n'
    )
    for file in staged.rglob('*.py'):
        compile(file.read_text(), str(file), 'exec')
    env = dict(os.environ, PYTHONPATH=str(Path(temp)), PYTHONDONTWRITEBYTECODE='1',
               HEALTHLINK_PROJECT_ROOT=str(root))
    result = subprocess.run([sys.executable, '-c',
        'import app.main; from app.prompts import load_healthlink_prompt; '
        'assert load_healthlink_prompt(); print("Imports and prompt loading passed")'],
        cwd=temp, env=env, capture_output=True, text=True)
    if result.returncode:
        # Avoid exposing exception values which might contain configuration secrets.
        error_lines = [line for line in result.stderr.splitlines() if line.strip()]
        error_type = error_lines[-1].split(':', 1)[0] if error_lines else 'unknown error'
        stop('Staged app import failed (' + error_type + '). No source changed. '
             'Check that the existing app runs with this venv and .env; share this error type.')
    print(result.stdout.strip())
    for name, destination in moves.items():
        if name + '.py' in sources:
            print(f'  {name}.py -> {destination.replace(".", "/")}.py')
    print('  Extract: schemas, tools/definitions.py, prompts/healthlink.txt, core/config.py')
    print('  Old module paths retained as compatibility wrappers where needed.')
    if mode == '--check':
        print('\nCHECK PASSED. No project source changed. Stop backend, then run with --apply.')
    else:
        backup = backups / datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True)
        (backup / 'REFRACTOR_BACKUP').write_text(str(root))
        app.rename(backup / 'app')
        try:
            shutil.copytree(staged, app)
        except BaseException:
            if app.exists():
                shutil.rmtree(app)
            (backup / 'app').rename(app)
            raise
        print('\nAPPLIED. Original backend/app backup:', backup)
        print('Rollback: bash restructure_healthlink.sh --restore "' + str(backup) + '"')
        print('Start: python -m uvicorn app.main:app --app-dir backend --reload --port 8000')
        print('Still required: live health/readiness, chat, slots, booking smoke checks.')
        print('No database, frontend, dependency, .env or deployment file was changed.')
PY
