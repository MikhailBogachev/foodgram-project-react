from django.db.models import Model, Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)


class AddOrDeleteRelationForUserViewMixin:
    """Миксин для работы со связями между пользователем и объектом"""
    relation_serializer: ModelSerializer
    relation_model: Model

    def add_relation(self, object_id: int) -> Response:
        """Добавляет связь"""
        obj = get_object_or_404(self.queryset, pk=object_id)
        entry = self.relation_model(None, self.request.user.pk, obj.pk,)
        try:
            entry.save()
        except IntegrityError:
            return Response(
                data={"error": "Связь уже сущветвует"},
                status=HTTP_400_BAD_REQUEST,
            )
        serializer = self.relation_serializer(obj)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete_relation(self, params: Q) -> Response:
        """Удаляет свзяь"""
        obj = self.relation_model.objects.filter(
            params & Q(user=self.request.user)
        )
        status, _ = obj.delete()
        if not status:
            return Response(
                data={"error": "Связи не существует"},
                status=HTTP_400_BAD_REQUEST,
            )
        return Response(status=HTTP_204_NO_CONTENT)
