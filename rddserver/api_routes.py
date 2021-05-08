from flask_restful import Resource
from rddserver import api


API_URL = "/api"

class IssueResource(Resource):
    def get(self):
        return {'message': 'hello'}

    def post(self, request):
        pass
        



api.add_resource(IssueResource, f'{API_URL}/issue')
