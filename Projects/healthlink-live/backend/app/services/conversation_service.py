from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.db.database import engine
from app.db.models import Conversation, Message


class ConversationNotFound(Exception):
    pass


class ConversationBusy(Exception):
    pass


def create_conversation():
    with Session(engine) as session:
        conversation = Conversation(patient_id="demo-patient")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return {
            "id": conversation.id,
            "patient_id": conversation.patient_id,
            "created_at": conversation.created_at,
        }
    


def get_messages(conversation_id: str):
    with Session(engine) as session:
        if session.get(Conversation, conversation_id) is None:
            raise ConversationNotFound()
        messages = session.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.id.asc())
        ).all()
        return [
            {
                "id": item.id,
                "role": item.role,
                "content": item.content,
                "status": item.status,
                "created_at": item.created_at,
            }
            for item in messages
        ]



def prepare_turn(conversation_id: str, content: str):
    with Session(engine) as session:
        with session.begin():
            conversation = session.scalar(
                select(Conversation)
                .where(Conversation.id == conversation_id)
                .with_for_update()
            )
            if conversation is None:
                raise ConversationNotFound()
            pending_id = session.scalar(
                select(Message.id)
                .where(
                    Message.conversation_id == conversation_id,
                    Message.status == "pending",
                )
                .limit(1)
            )
            if pending_id is not None:
                raise ConversationBusy()
            previous = session.scalars(
                select(Message)
                .where(
                    Message.conversation_id == conversation_id,
                    Message.status == "completed",
                )
                .order_by(Message.id.desc())
                .limit(20)
            ).all()
            history = [
                {"role": item.role, "content": item.content}
                for item in reversed(previous)
            ]
            user_message = Message(
                conversation_id=conversation_id,
                role="user",
                content=content,
                status="pending",
            )
            session.add(user_message)
            session.flush()
            message_id = user_message.id
        return message_id, history


def complete_turn(message_id: int, reply: str):
    with Session(engine) as session:
        with session.begin():
            user_message = session.get(Message, message_id)
            if user_message is None or user_message.status != "pending":
                raise ValueError("Turn is not pending")
            user_message.status = "completed"
            session.add(
                Message(
                    conversation_id=user_message.conversation_id,
                    role="assistant",
                    content=reply,
                    status="completed",
                )
            )


def fail_turn(message_id: int):
    with Session(engine) as session:
        with session.begin():
            session.execute(
                update(Message)
                .where(Message.id == message_id, Message.status == "pending")
                .values(status="failed")
            )




