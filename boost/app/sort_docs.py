from django.db.models import Q
from app.models import Doc


class SortDocs:
    SORT_TYPES = ['-likes', '-dislikes', '-date', 'date']

    def __init__(self, request):
        self.sort_type = None
        self.query_studies = Q()
        self.query_subjects = Q()
        self.query_title = Q()
        self.query_description = Q()

        self.search = request.GET.get('q')
        self.studies = list(request.GET.getlist('studies'))
        self.subjects = list(request.GET.getlist('subjects'))
        self.sort_type_get = request.GET.get('sort_type')

    def convert(self):
        if self.sort_type_get:
            self.sort_type = self.SORT_TYPES[int(self.sort_type_get) - 1]
        else:
            self.sort_type = '-pk'

        if self.subjects:
            self.query_subjects = Q(subjects__in=self.subjects)

        if self.studies:
            self.query_studies = Q(studies__in=self.studies)

        if self.search:
            self.query_title = Q(
                title__contains=self.search.lower()
            )
            self.query_description = Q(
                description__contains=self.search.lower()
            )

    def make_request(self, docs=Doc.objects.all()):
        docs = docs.filter(
            self.query_subjects & self.query_studies & (self.query_title | self.query_description)
        ).order_by(self.sort_type)

        return docs
