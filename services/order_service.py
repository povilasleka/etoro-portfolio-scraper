from typing import List, Tuple
from models import Portfolio, Position


class OrderService:
    @staticmethod
    def sync_orders(scraped_orders: List[Position], portfolio: Portfolio) -> Tuple[List[Position], List[Position]]:
        """
        Synchronize scraped orders with database for a specific portfolio.
        Creates new orders and deletes orders no longer present.

        Returns:
            Tuple[List[Position], List[Position]]: (orders_created, orders_deleted)
        """
        print(f"Portfolio has {portfolio.positions.count()} orders before sync")

        # Get orders to create
        positions_to_create = OrderService._get_orders_to_create(scraped_orders, portfolio)

        if positions_to_create:
            Position.bulk_create(positions_to_create)

        # Get orders to delete
        positions_to_delete = OrderService._get_orders_to_delete(scraped_orders, portfolio)

        for order in positions_to_delete:
            order.delete_instance()

        print(f"Portfolio has {portfolio.positions.count()} orders after sync")

        return positions_to_create, positions_to_delete

    @staticmethod
    def _get_orders_to_create(orders: List[Position], portfolio: Portfolio) -> List[Position]:
        """Get orders that exist in scraped data but not in database for this portfolio."""
        positions_to_create = []
        for order in orders:
            db_order = Position.get_or_none(
                (Position.hash_value == order.hash_value) &
                (Position.portfolio == portfolio)
            )
            if db_order is None:
                positions_to_create.append(order)
        return positions_to_create

    @staticmethod
    def _get_orders_to_delete(orders: List[Position], portfolio: Portfolio) -> List[Position]:
        """Get orders that exist in database but not in scraped data for this portfolio."""
        scraped_hashes = {order.hash_value for order in orders}
        positions_to_delete = []

        for db_order in portfolio.positions:
            if db_order.hash_value not in scraped_hashes:
                positions_to_delete.append(db_order)

        return positions_to_delete