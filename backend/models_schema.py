from pydantic import BaseModel
from typing import List
from tortoise.models import Model
from tortoise import fields
import uuid

class Escalating(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    question = fields.CharField(max_length=100)
    email = fields.CharField(max_length=255)
    is_escalated =fields.BooleanField(default=False)
    escalation_reason=fields.CharField(max_length=500,null=True, default=None)
    
    
