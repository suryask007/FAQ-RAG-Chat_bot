import uvicorn
from fastapi import FastAPI,UploadFile,File,middleware
from fastapi.middleware.cors import CORSMiddleware
from backend.llm_ import rag_llm
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise
# from try_task.database import SessionLocal
# from try_task.models_schema import Analytics
from backend.inent_detemain import detect_escalation_need
from backend.models_schema import Escalating
import random
from backend.email_page import admin_assign,customer_support
app=FastAPI()
register_tortoise(
    app,
    db_url="postgres://postgres:root@localhost:5432/postgres",  # Change as needed
    modules={"models": ["main"]},  # Point to the current file/module
    generate_schemas=True,  # Auto-generate tables
    add_exception_handlers=True,  # Add error handlers for database operations
)
origins = [
    "*"
]

# These lines configure CORS middleware to allow cross-origin requests from any origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/model")
async def main(input,email):
    bot_response, intent, confidence=rag_llm(input)
    needs_escalation, escalation_reason = detect_escalation_need(input, intent, confidence)
    random_number = random.randrange(100000)
    rad={"random":random_number}
    if needs_escalation:
        # conversation.escalated = True
        bot_response += f"\n\nI'll connect you with a human agent who can better assist with this question. {escalation_reason}"
        cad=customer_support(rad["random"],email)
        ad=admin_assign(rad["random"],"enrollments24@gmail.com",email,input)

    data = {
    "question": input,
    "email": email,
    "is_escalated":needs_escalation,
    "escalation_reason":escalation_reason
    }

    user_obj = await Escalating.create(**data)
    return JSONResponse({
        'message': bot_response,
        'needs_escalation': needs_escalation,
        'intent': intent
    })


@app.get("/analytics/update")
async def analyist():
    # s=await Escalating.all()
    # m=0
    # for details_len in s:
    #     print(details_len.is_escalated)
    #     if details_len.is_escalated== True:
    #         m+=1
    # full_details={"is_escalated":m}      
    # return full_details

    is_escalated_list = await Escalating.all().values_list("is_escalated", flat=True)

    # Count escalated and total
    total_count = len(is_escalated_list)
    escalated_count = sum(is_escalated_list)

    return {
        "total": total_count,
        "escalated": escalated_count,
        "not_escalated": total_count - escalated_count
    }



if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=8050)