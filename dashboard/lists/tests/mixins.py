

class UpdateListMixin(object):

    def _create_list_dictionary(self, list_obj):
        dictionary = {
            "ancestor": list_obj.ancestor.id if list_obj.ancestor else None,
            "creation_date": list_obj.creation_date.isoformat(),
            "description": list_obj.description,
            "is_inbox": list_obj.is_inbox,
            "logo": list_obj.logo.url,
            "modification_date": list_obj.modification_date.isoformat(),
            "name": list_obj.name,
            "owner": list_obj.owner.id,
            "color": list_obj.color,
            "share_with": list(map( lambda x: {'id': str(x)}, list_obj.share_with.all().values_list("id", flat=True))),
            "default_priority": "C",
            "is_active": list_obj.is_active,
            "default_task_view": list_obj.default_task_view
        }
        return dictionary