"""Tests for the intent-based query router."""

import pytest

from app.agent.router import QueryClassification, QueryIntent, classify_query


class TestQueryClassification:
    """Tests for the QueryClassification model."""

    def test_valid_customer_support_classification(self):
        """Test creating a valid customer support classification."""
        classification = QueryClassification(
            intent=QueryIntent.CUSTOMER_SUPPORT,
            confidence=0.95,
            reason="Question about order returns",
        )
        assert classification.intent == QueryIntent.CUSTOMER_SUPPORT
        assert classification.confidence == 0.95

    def test_valid_off_topic_classification(self):
        """Test creating a valid off-topic classification."""
        classification = QueryClassification(
            intent=QueryIntent.OFF_TOPIC,
            confidence=0.99,
            reason="General knowledge question",
        )
        assert classification.intent == QueryIntent.OFF_TOPIC
        assert classification.confidence == 0.99

    def test_confidence_bounds(self):
        """Test that confidence must be between 0 and 1."""
        with pytest.raises(ValueError):
            QueryClassification(
                intent=QueryIntent.OFF_TOPIC,
                confidence=1.5,
                reason="Invalid confidence",
            )

        with pytest.raises(ValueError):
            QueryClassification(
                intent=QueryIntent.OFF_TOPIC,
                confidence=-0.1,
                reason="Invalid confidence",
            )


class TestClassifyQuery:
    """Integration tests for the classify_query function.

    These tests call the actual OpenAI API and verify classification behavior.
    """

    @pytest.mark.parametrize(
        "query",
        [
            "How do I return an item?",
            "What is your refund policy?",
            "Where is my order?",
            "How can I track my shipment?",
            "What payment methods do you accept?",
            "I need help with my account",
            "Can I cancel my order?",
            "How long does shipping take?",
        ],
    )
    def test_customer_support_queries(self, query: str):
        """Test that customer support queries are classified correctly."""
        result = classify_query(query)

        assert isinstance(result, QueryClassification)
        assert result.intent == QueryIntent.CUSTOMER_SUPPORT
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.reason) > 0

    @pytest.mark.parametrize(
        "query",
        [
            "Who is the president of the United States?",
            "What is the capital of France?",
            "How do I write a Python function?",
            "What is the meaning of life?",
            "Tell me a joke",
            "What is 2 + 2?",
            "Who won the World Cup in 2022?",
            "Explain quantum physics",
        ],
    )
    def test_off_topic_queries(self, query: str):
        """Test that off-topic queries are classified correctly."""
        result = classify_query(query)

        assert isinstance(result, QueryClassification)
        assert result.intent == QueryIntent.OFF_TOPIC
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.reason) > 0

    def test_classification_returns_reason(self):
        """Test that classification always includes a reason."""
        result = classify_query("What is the weather like?")

        assert result.reason is not None
        assert len(result.reason) > 0

    def test_empty_query_handling(self):
        """Test handling of empty or whitespace queries."""
        result = classify_query("")

        assert isinstance(result, QueryClassification)
        assert result.intent in [QueryIntent.CUSTOMER_SUPPORT, QueryIntent.OFF_TOPIC]
