// A small safe formatter: text, bold, bullet/numbered lines. No HTML execution.
function inline(text) {
 return text.split(/(\*\*[^*]+\*\*)/g).map((part,i)=>part.startsWith('**')&&part.endsWith('**') ? <strong key={i}>{part.slice(2,-2)}</strong> : part);
}
export default function MessageContent({text}) {
 return <div className="message-content">{String(text).split('\n').map((line,i)=><div className={/^\s*[-*]\s/.test(line)?'bullet':'text-line'} key={i}>{inline(line.replace(/^\s*[-*]\s/,'• ')) || <br/>}</div>)}</div>;
}
