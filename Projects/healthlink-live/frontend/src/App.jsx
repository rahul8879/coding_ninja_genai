import {useState,useRef,useEffect} from 'react';
import {createConversation,getMessages,sendMessage} from './api';
import {read,write,proposalKey} from './storage';
import BookingConfirmation from './BookingConfirmation';
import MessageContent from './MessageContent';
import Icon from './Icon';
const SESSION='healthlink.activeConversation';
const suggestions=['Find a dermatologist','Help me choose a specialist','How do I book an appointment?'];
export default function App(){
 const [conversationId,setConversationId]=useState(()=>read(SESSION,''));
 const [messages,setMessages]=useState([]),[draft,setDraft]=useState('');
 const [busy,setBusy]=useState(false),[historyReady,setHistoryReady]=useState(false),[error,setError]=useState('');
 const [proposal,setProposal]=useState(()=>read(proposalKey(read(SESSION,''))));
 const [bookingBlocked,setBookingBlocked]=useState(false),[reload,setReload]=useState(0);
 const inFlight=useRef(false),bottom=useRef(null),bookingRef=useRef(null),textarea=useRef(null);
 useEffect(()=>{
  let cancelled=false;setMessages([]);setHistoryReady(false);setError('');
  if(!conversationId)return;
  getMessages(conversationId).then(data=>{if(!cancelled){setMessages(data.messages);setHistoryReady(true);}}).catch(err=>{if(!cancelled)setError(err.message);});
  return()=>{cancelled=true};
 },[conversationId,reload]);
 useEffect(()=>{bottom.current?.scrollIntoView({behavior:'smooth',block:'nearest'});},[messages,busy]);
 useEffect(()=>{if(proposal)bookingRef.current?.scrollIntoView({behavior:'smooth',block:'nearest'});},[proposal]);
 async function startNewChat(){
  if(inFlight.current||busy||bookingBlocked||proposal)return;
  inFlight.current=true;setBusy(true);setError('');
  try{const data=await createConversation();write(SESSION,data.id);setConversationId(data.id);setHistoryReady(false);setDraft('');setProposal(null);setBookingBlocked(false);}
  catch(err){setError(err.message);}finally{inFlight.current=false;setBusy(false);}
 }
 async function handleSend(e){
  e.preventDefault();const message=draft.trim();
  if(!message||!conversationId||!historyReady||busy||proposal||inFlight.current)return;
  inFlight.current=true;setBusy(true);setError('');
  try{
   const result=await sendMessage(conversationId,message);setDraft('');
   if(result.booking_proposal){write(proposalKey(conversationId),result.booking_proposal);setProposal(result.booking_proposal);}
  }catch(err){setError(err.message);}finally{
   try{const data=await getMessages(conversationId);setMessages(data.messages);}
   catch{setHistoryReady(false);setError('History could not be refreshed. Reload history before sending another message.');}
   inFlight.current=false;setBusy(false);
  }
 }
 function dismiss(){if(bookingBlocked)return;write(proposalKey(conversationId),null);setProposal(null);}
 const disabled=!conversationId||!historyReady||busy||!!proposal;
 const phase=proposal?2:messages.length?1:0;
 return <div className="app-layout">
  <aside className="sidebar"><a className="brand" href="#main"><span className="brand-icon"><Icon name="plus" size={23}/></span><span>HealthLink<span className="brand-sub">CARE, CONNECTED.</span></span></a>
   <button className="new-chat" onClick={startNewChat} disabled={busy||!!proposal||bookingBlocked}><Icon name="plus"/>New conversation</button>
   <p className="nav-label">YOUR WORKSPACE</p><div className="nav-active"><Icon name="chat"/>Care assistant<span className="nav-dot"/></div>
   <div className="sidebar-info"><Icon name="shield" size={24}/><h3>A little guidance.<br/>A clearer next step.</h3><p>Find a specialist, explore available times, and confirm your appointment.</p></div>
   <div className="patient"><div className="avatar">DP</div><div><strong>Demo patient</strong><span>Single-patient workspace</span></div></div>
  </aside>
  <main id="main" className="main"><header className="topbar"><div><p className="eyebrow">YOUR HEALTHCARE WORKSPACE</p><h1>Care assistant</h1></div><div className="top-actions"><span className="top-badge"><Icon name="shield" size={16}/>Care navigation</span><button className="mobile-new" aria-label="New conversation" onClick={startNewChat} disabled={busy||!!proposal||bookingBlocked}><Icon name="plus" size={18}/></button></div></header>
   <div className="workspace"><section className="chat-panel" aria-label="Care conversation"><div className="chat-heading"><div className="assistant-icon"><Icon name="plus"/></div><div><strong>HealthLink Assistant</strong><p>Let’s find the right next step.</p></div><span className="session-label">{conversationId?'Conversation open':'Ready to start'}</span></div>
    <div className="message-area" aria-busy={busy}>
     {!messages.length&&<div className="welcome"><div className="welcome-symbol"><Icon name="heart" size={32}/></div><p className="eyebrow">WELCOME TO HEALTHLINK</p><h2>Better care starts<br/>with a conversation.</h2><p>Tell us what’s on your mind.<br/>We’ll help you explore relevant care options.</p>
     {!conversationId?<button className="primary" onClick={startNewChat} disabled={busy}>Start a conversation<Icon name="arrow"/></button>:!historyReady?<p role="status">Loading conversation…</p>:<div className="suggestions">{suggestions.map(s=><button key={s} onClick={()=>{setDraft(s);textarea.current?.focus();}} disabled={disabled}>{s}<Icon name="arrow" size={16}/></button>)}</div>}</div>}
     {messages.map(m=><article className={`message ${m.role==='user'?'user':'assistant'}`} key={m.id}><div className="message-avatar">{m.role==='user'?'You':<Icon name="plus" size={18}/>}</div><div className="message-main"><div className="message-meta"><strong>{m.role==='user'?'You':'HealthLink'}</strong><time dateTime={m.created_at}>{new Date(m.created_at).toLocaleTimeString('en-IN',{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit'})} IST</time></div><div className="bubble"><MessageContent text={m.content}/></div>{m.status==='failed'&&<small className="failed">This turn failed. Check the error before retrying.</small>}{m.status==='pending'&&<small>Reply pending. Refresh history to check its status.</small>}</div></article>)}
     {busy&&<div className="working" role="status"><span className="spinner"/>Working on your request…</div>}<div ref={bottom}/>
    </div>
    <div className="composer-wrap">{error&&<div className="error" role="alert">{error}{conversationId&&!historyReady&&<button className="quiet" disabled={busy} onClick={()=>setReload(v=>v+1)}>Reload history</button>}</div>}
     {proposal&&<div className="action-notice"><Icon name="calendar" size={17}/><span>Review the appointment card to confirm or dismiss before continuing.</span></div>}
     <form onSubmit={handleSend} className="composer"><textarea ref={textarea} aria-label="Your message" placeholder={proposal?'Review your appointment card…':conversationId?'Describe your concern or ask a question…':'Start a conversation to send a message…'} value={draft} maxLength={2000} rows={2} disabled={disabled} onChange={e=>setDraft(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.nativeEvent.isComposing){e.preventDefault();if(!disabled&&draft.trim())e.currentTarget.form.requestSubmit();}}}/><button className="send-button" type="submit" aria-label="Send message" disabled={disabled||!draft.trim()}><Icon name="send"/></button></form>
     <div className="composer-footer"><span>Enter to send · Shift + Enter for a new line</span><span>{draft.length}/2,000</span></div>
    </div>
   </section>
   <aside className="context-panel"><div ref={bookingRef}>{proposal?<BookingConfirmation key={proposal.proposal_id} conversationId={conversationId} proposal={proposal} onBlockedChange={setBookingBlocked} onDismiss={dismiss}/>:<section className="journey"><p className="eyebrow">A SIMPLE PATH TO CARE</p><h2>Your next steps</h2>{[['Share your concern','Tell us what you need help with.'],['Explore care options','Find a doctor and check available slots.'],['Review & confirm','Use the confirmation card to book.']].map(([t,d],i)=><div className={`journey-step ${i===phase?'current':''}`} key={t}><span>{i+1}</span><div><h3>{t}</h3><p>{d}</p></div></div>)}</section>}</div>
    <section className="care-note"><Icon name="shield" size={22}/><h3>Guidance, with clear limits</h3><p>HealthLink helps you navigate care. It does not provide a diagnosis or replace a clinician.</p><p>For an emergency, contact your local emergency service.</p></section>
    <div className="timezone"><Icon name="clock" size={16}/>Appointment times shown in IST</div>
   </aside></div>
   <footer className="page-footer"><span>HealthLink · Care navigation workspace</span><span>Powered by your connected care directory</span></footer>
  </main>
 </div>;
}
