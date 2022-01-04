from utils.graphene.tests import GraphQLTestCase
from apps.user.factories import UserFactory
from django.contrib.auth.hashers import check_password


class TestUser(GraphQLTestCase):
    def setUp(self):
        self.register_mutation = '''
            mutation Mutation($input: RegisterInputType!) {
                register(data: $input) {
                    ok
                    result {
                        email
                        id
                        firstName
                        lastName
                    }
                }
            }
        '''
        self.login_mutation = '''
        mutation Mutation($input: LoginInputType!) {
            login(data: $input) {
                ok
                result {
                    email
                    id
                }
            }
        }
        '''
        self.change_password_mutation = '''
            mutation Mutation($input: UserPasswordInputType!) {
                changePassword(data: $input) {
                    ok
                    result {
                        email
                    }
                }
            }
        '''
        self.logout_mutation = '''
            mutation Mutation {
              logout {
                ok
              }
            }
        '''
        super().setUp()

    def test_register(self):
        minput = {"firstName": "Rosy", "lastName": "Rosy", "email": "rosy@gmail.com", "password": "nsPzXEVKGCIriVu"}
        content = self.query_check(self.register_mutation, minput=minput, okay=True)
        self.assertEqual(content['data']['register']['result']['firstName'], minput['firstName'], content)
        self.assertEqual(content['data']['register']['result']['lastName'], minput['lastName'], content)
        self.assertEqual(content['data']['register']['result']['email'], minput['email'], content)

    def test_login(self):
        # Test invaid user should not login
        minput = {"email": "alex@gmail.com", "password": "rupoFpCyZVaNMjY"}
        self.query_check(self.login_mutation, minput=minput, okay=False)

        # Test valid user should login
        user = UserFactory.create(email=minput['email'])
        minput = {"email": user.email, "password": user.password_text}
        content = self.query_check(self.login_mutation, minput=minput, okay=True)
        self.assertEqual(content['data']['login']['result']['id'], str(user.id), content)
        self.assertEqual(content['data']['login']['result']['email'], user.email, content)

    def test_change_password(self):
        user = UserFactory.create()
        self.force_login(user)
        new_password = "INZbHBhOyCqurWt"
        minput = {"oldPassword": user.password_text, "newPassword": new_password}
        self.query_check(self.change_password_mutation, minput=minput, okay=True)
        user.refresh_from_db()
        self.assertTrue(check_password(new_password, user.password))

    def test_logout(self):
        self.query_check(self.logout_mutation, okay=True)
