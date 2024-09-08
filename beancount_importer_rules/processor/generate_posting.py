import typing

from beancount_importer_rules.data_types import (
    Amount,
    GeneratedPosting,
    PostingTemplate,
)


def generate_postings(
    posting_templates: list[PostingTemplate], render_str: typing.Callable
) -> list[GeneratedPosting]:
    generated_postings = []
    for posting_template in posting_templates:
        amount = None
        if posting_template.amount is not None:
            amount = Amount(
                number=render_str(posting_template.amount.number),
                currency=render_str(posting_template.amount.currency),
            )
        price = None
        if posting_template.price is not None:
            price = Amount(
                number=render_str(posting_template.price.number),
                currency=render_str(posting_template.price.currency),
            )
        cost = None
        if posting_template.cost is not None:
            cost = render_str(posting_template.cost)
        generated_postings.append(
            GeneratedPosting(
                account=render_str(posting_template.account),
                amount=amount,
                price=price,
                cost=cost,
            )
        )
    return generated_postings
