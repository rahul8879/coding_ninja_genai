import { useState, useRef, useEffect } from 'react';
import { bookAppointment } from './api';
import { read, write } from './storage';
import Icon from './Icon';
const date = value => new Date(value).toLocaleDateString('en-IN',{timeZone:'Asia/Kolkata',weekday:'long',day:'numeric',month:'long',year:'numeric'});
const time = value => new Date(value).toLocaleTimeString('en-IN',{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit'});
export default function BookingConfirmation({conversationId,proposal,onBlockedChange,onDismiss}) {
 const key=`healthlink.receipt.${conversationId}.${proposal.proposal_id}`;
 const [saved,setSaved]=useState(()=>read(key,{status:'review',appointment:null}));
 const [busy,setBusy]=useState(false), [error,setError]=useState('');
 const inFlight=useRef(false);
 const uncertain=saved.status==='uncertain';
 const confirmed=saved.status==='confirmed';
 const rejected=saved.status==='rejected';
 useEffect(()=>{onBlockedChange(busy||uncertain);},[busy,uncertain,onBlockedChange]);
 function update(next){write(key,next);setSaved(next);}
 async function confirm(){
  if(inFlight.current||confirmed||rejected)return;
  inFlight.current=true;setBusy(true);setError('');
  // Save the same proposal/key before sending. Reload can retry safely.
  update({status:'uncertain',appointment:null});
  try {
   const result=await bookAppointment({conversation_id:conversationId,doctor_id:proposal.doctor_id,starts_at:proposal.starts_at,idempotency_key:proposal.proposal_id});
   if(!result.appointment_id)throw new Error('Missing appointment receipt');
   update({status:'confirmed',appointment:result});
  } catch(err){
   if([400,404,409,422].includes(err.status)){
    update({status:'rejected',appointment:null});setError(err.message);
   }else {update({status:'uncertain',appointment:null});setError('The result could not be verified. Retry the same confirmation request safely.');}
  }finally{inFlight.current=false;setBusy(false);}
 }
 return <section className="booking-card" aria-labelledby="booking-title">
  <div className={`booking-banner ${confirmed?'success':''}`}><Icon name={confirmed?'check':'calendar'}/><span>{confirmed?'BOOKING RECEIPT':'ACTION REQUIRED'}</span></div>
  <div className="booking-body"><h3 id="booking-title">{confirmed?'Appointment confirmed':rejected?'Slot could not be booked':uncertain?'Check booking result':'Review your appointment'}</h3>
   <p className="doctor-name">{proposal.doctor_name}</p>
   <div className="booking-detail"><Icon name="calendar"/><span>{date(proposal.starts_at)}</span></div>
   <div className="booking-detail"><Icon name="clock"/><span>{time(proposal.starts_at)} – {time(proposal.ends_at)} IST</span></div>
   {confirmed ? <div className="receipt" role="status"><strong>Saved successfully</strong><span>Appointment ID</span><code>{saved.appointment.appointment_id}</code></div> : <p className="booking-help">{uncertain?'The previous request may have completed. Retrying uses the same booking key and will not create a duplicate.':rejected?'Close this card and ask for available slots again.':'The slot is checked again when you confirm. Typing “yes” in chat does not book it.'}</p>}
   {error&&<p className="error" role="alert">{error}</p>}
   {!confirmed&&!rejected&&<button className="primary full" onClick={confirm} disabled={busy}>{busy?'Confirming…':uncertain?'Retry confirmation':'Confirm booking'}<Icon name="arrow"/></button>}
   <button className="quiet full" onClick={onDismiss} disabled={busy||uncertain}>{confirmed?'Close receipt & continue':rejected?'Close & choose another slot':'Dismiss & continue chatting'}</button>
  </div>
 </section>;
}
