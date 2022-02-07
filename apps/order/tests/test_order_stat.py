import datetime
from apps.common.tests.test_permissions import TestPermissions
from apps.user.models import User
from apps.order.models import Order

from apps.user.factories import UserFactory
from apps.book.factories import BookFactory
from apps.publisher.factories import PublisherFactory
from apps.order.factories import OrderFactory, BookOrderFactory


class TestOrderState(TestPermissions):
    def setUp(self):
        super(TestOrderState, self).setUp()
        self.order_stat = '''
            query MyQuery {
              orderStat {
                booksOrderedCount
                booksUploadedCount
                ordersCompletedCount
                totalQuantity
                stat {
                  totalPrice
                  totalQuantity
                }
              }
            }
        '''
        stat_to = datetime.date.today()
        stat_from = stat_to - datetime.timedelta(30)
        intermediate_date = stat_to - datetime.timedelta(15)
        not_in_range_date = stat_to - datetime.timedelta(40)

        # Create publishers
        self.publisher_1 = PublisherFactory.create()
        self.publisher_2 = PublisherFactory.create()

        # Create publisher users
        self.publisher_user_1 = UserFactory.create(
            user_type=User.UserType.PUBLISHER, publisher=self.publisher_1
        )
        self.publisher_user_2 = UserFactory.create(
            user_type=User.UserType.PUBLISHER, publisher=self.publisher_2
        )

        # Create 4 book in different date range
        self.book_1 = BookFactory.create(publisher=self.publisher_1, published_date=stat_to)
        self.book_2 = BookFactory.create(publisher=self.publisher_1, published_date=stat_from)
        self.book_3 = BookFactory.create(publisher=self.publisher_2, published_date=intermediate_date)
        self.book_4 = BookFactory.create(publisher=self.publisher_2, published_date=not_in_range_date)

        # Create 3 book orders
        order_1 = OrderFactory.create(created_by=self.individual_user, status=Order.OrderStatus.COMPLETED)
        order_2 = OrderFactory.create(created_by=self.individual_user, status=Order.OrderStatus.COMPLETED)
        order_3 = OrderFactory.create(created_by=self.individual_user, status=Order.OrderStatus.COMPLETED)

        # Create 4 book orders each having 5 quantity and 500 price
        BookOrderFactory.create(
            order=order_1, publisher=self.publisher_1, book=self.book_1, quantity=5, price=500
        )
        BookOrderFactory.create(
            order=order_2, publisher=self.publisher_1, book=self.book_2, quantity=5, price=500
        )
        BookOrderFactory.create(
            order=order_3, publisher=self.publisher_2, book=self.book_3, quantity=5, price=500
        )
        super().setUp()

    def test_admin_can_see_overall_stat(self):
        self.force_login(self.super_admin)
        content = self.query_check(self.order_stat)
        order_stat = content['data']['orderStat']
        # Test shoudl retrive correct count
        self.assertEqual(order_stat['booksOrderedCount'], 3)
        self.assertEqual(order_stat['booksUploadedCount'], 4)
        self.assertEqual(order_stat['ordersCompletedCount'], 3)

        # Test shoudl retrive quantity count
        self.assertEqual(len(order_stat['stat']), 3)
        self.assertEqual(order_stat['stat'][0]['totalQuantity'], 5)
        self.assertEqual(order_stat['stat'][1]['totalQuantity'], 5)
        self.assertEqual(order_stat['stat'][2]['totalQuantity'], 5)

    def test_publisher_can_see_their_stat_only(self):
        # ------------------------------------
        # Test for first publisher
        # ------------------------------------
        self.force_login(self.publisher_user_1)
        content = self.query_check(self.order_stat)
        order_stat = content['data']['orderStat']
        # Test shoudl retrive correct count
        self.assertEqual(len(order_stat['stat']), 2)
        self.assertEqual(order_stat['booksOrderedCount'], 2)
        self.assertEqual(order_stat['booksUploadedCount'], 2)
        self.assertEqual(order_stat['ordersCompletedCount'], 2)

        # Test shoudl retrive quantity count
        self.assertEqual(order_stat['stat'][0]['totalQuantity'], 5)
        self.assertEqual(order_stat['stat'][1]['totalQuantity'], 5)

        # ------------------------------------
        # Test second first publisher
        # ------------------------------------
        self.force_login(self.publisher_user_1)
        content = self.query_check(self.order_stat)
        order_stat = content['data']['orderStat']
        self.assertEqual(len(order_stat['stat']), 2)
        self.assertEqual(order_stat['booksOrderedCount'], 2)
        self.assertEqual(order_stat['booksUploadedCount'], 2)
        self.assertEqual(order_stat['ordersCompletedCount'], 2)
        self.assertEqual(order_stat['stat'][0]['totalQuantity'], 5)
        self.assertEqual(order_stat['stat'][1]['totalQuantity'], 5)

    def test_school_admin_can_see_their_stat_only(self):
        order = OrderFactory.create(created_by=self.school_admin_user, status=Order.OrderStatus.COMPLETED)
        BookOrderFactory.create(
            order=order, publisher=self.publisher_1, book=self.book_1, quantity=10, price=100
        )
        self.force_login(self.school_admin_user)
        content = self.query_check(self.order_stat)
        order_stat = content['data']['orderStat']
        self.assertEqual(len(order_stat['stat']), 1)
        self.assertEqual(order_stat['booksOrderedCount'], 1)
        self.assertEqual(order_stat['booksUploadedCount'], 0)
        self.assertEqual(order_stat['ordersCompletedCount'], 1)
        self.assertEqual(order_stat['stat'][0]['totalQuantity'], 10)

    def test_individual_user_can_see_their_stat_only(self):
        order = OrderFactory.create(created_by=self.individual_user, status=Order.OrderStatus.COMPLETED)
        BookOrderFactory.create(
            order=order, publisher=self.publisher_1, book=self.book_1, quantity=30, price=100
        )
        self.force_login(self.individual_user)
        content = self.query_check(self.order_stat)
        order_stat = content['data']['orderStat']
        self.assertEqual(len(order_stat['stat']), 1)
        self.assertEqual(order_stat['booksOrderedCount'], 1)
        self.assertEqual(order_stat['booksUploadedCount'], 0)
        self.assertEqual(order_stat['ordersCompletedCount'], 1)
        self.assertEqual(order_stat['stat'][0]['totalQuantity'], 30)
