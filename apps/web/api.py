from typing import List

from ninja import Router, ModelSchema, Schema
from ninja_apikey.models import APIKey

router = Router()


class APIKeySchema(ModelSchema):
    class Meta:
        model = APIKey
        fields = ("prefix", "label", "revoked", "created_at")


class CreateAPIKeyIn(Schema):
    label: str


class APIKeyResponseSchema(Schema):
    key: str
    prefix: str
    label: str


@router.get("/", response=List[APIKeySchema])
def list_api_keys(request):
    return list(APIKey.objects.filter(user=request.user).order_by("-created_at"))


@router.post("/", response=APIKeyResponseSchema)
def create_api_key(request, data: CreateAPIKeyIn):
    key = request.user.create_api_key(label=data.label)
    prefix = key.split(".")[0]
    return {"key": key, "prefix": prefix, "label": data.label}


@router.delete("/{prefix}")
def delete_api_key(request, prefix: str):
    key = APIKey.objects.filter(user=request.user, prefix=prefix).first()
    if not key:
        return {"success": False, "message": "Key not found"}

    key.revoked = True
    key.save()
    return {"success": True}
