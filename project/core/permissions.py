from rest_framework import permissions


class UsersOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class RelatedUserOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class ReceiverOrSenderOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user in [obj.sender == obj.receiver]
