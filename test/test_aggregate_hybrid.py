"""Unit tests for the GraphQL aggregate `hybrid` argument rendering.

These do not require a running Weaviate instance; they pin the exact GraphQL
fragments produced client-side.
"""

from weaviate.gql.aggregate import AggregateBuilder


def _build_hybrid(hybrid: dict) -> str:
    builder = AggregateBuilder("Article")
    builder.with_hybrid(hybrid)
    builder.with_fields("meta{count}")
    return builder.build()


def test_hybrid_without_query_does_not_emit_leading_comma() -> None:
    """The first hybrid argument must never be prefixed with a comma.

    Regression: the hybrid arguments were assembled by prepending ", " to every
    field after `query`. When `query` was omitted (which the public aggregate
    hybrid API allows, as `query` is typed optional), this produced a leading
    comma inside the input object, e.g. ``hybrid:{, vector: [0.1, 0.2]}``. That is
    not valid GraphQL and made the whole aggregate query fail to parse
    server-side, whereas a query-present hybrid rendered correctly.
    """
    cases = [
        ({"vector": [0.1, 0.2, 0.3]}, "hybrid:{vector: [0.1, 0.2, 0.3]}"),
        ({"alpha": 0.5}, "hybrid:{alpha: 0.5}"),
        ({"properties": ["title", "body"]}, 'hybrid:{properties: ["title","body"]}'),
    ]
    for hybrid, expected in cases:
        rendered = _build_hybrid(hybrid)
        assert expected in rendered, rendered
        assert "hybrid:{," not in rendered, rendered


def test_hybrid_with_query_renders_unchanged() -> None:
    """Query-present combinations must keep rendering exactly as before."""
    assert 'hybrid:{query: "hello"}' in _build_hybrid({"query": "hello"})
    assert 'hybrid:{query: "hello", vector: [0.1, 0.2]}' in _build_hybrid(
        {"query": "hello", "vector": [0.1, 0.2]}
    )
    assert 'hybrid:{query: "hi", targetVectors: ["tv"], maxVectorDistance:1.5}' in _build_hybrid(
        {"query": "hi", "targetVectors": ["tv"], "maxVectorDistance": 1.5}
    )
