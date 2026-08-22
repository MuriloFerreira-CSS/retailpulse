CREATE OR REPLACE VIEW analytics.vw_executive_overview AS
SELECT
    COUNT(DISTINCT s.session_id) AS sessions,
    COUNT(DISTINCT s.customer_key) AS customers,
    COUNT(DISTINCT o.order_id) AS orders,

    COALESCE(
        SUM(o.total_amount),
        0
    ) AS revenue,

    ROUND(
        COALESCE(
            AVG(o.total_amount),
            0
        ),
        2
    ) AS average_order_value,

    ROUND(
        COUNT(DISTINCT o.order_id)::NUMERIC
        / NULLIF(
            COUNT(DISTINCT s.session_id),
            0
        )
        * 100,
        2
    ) AS conversion_rate

FROM analytics.fact_sessions s

LEFT JOIN analytics.fact_orders o
    ON s.session_id = o.session_id;


CREATE OR REPLACE VIEW analytics.vw_funnel AS
SELECT
    COUNT(DISTINCT session_id) FILTER (
        WHERE event_type = 'page_view'
    ) AS page_view_sessions,

    COUNT(DISTINCT session_id) FILTER (
        WHERE event_type = 'product_view'
    ) AS product_view_sessions,

    COUNT(DISTINCT session_id) FILTER (
        WHERE event_type = 'add_to_cart'
    ) AS add_to_cart_sessions,

    COUNT(DISTINCT session_id) FILTER (
        WHERE event_type = 'checkout'
    ) AS checkout_sessions,

    COUNT(DISTINCT session_id) FILTER (
        WHERE event_type = 'purchase'
    ) AS purchase_sessions

FROM analytics.fact_events;


CREATE OR REPLACE VIEW analytics.vw_search_performance AS
SELECT
    search_term,

    COUNT(*) AS searches,

    COUNT(*) FILTER (
        WHERE results_count = 0
    ) AS zero_result_searches,

    ROUND(
        COUNT(*) FILTER (
            WHERE results_count = 0
        )::NUMERIC
        / NULLIF(
            COUNT(*),
            0
        )
        * 100,
        2
    ) AS zero_result_rate,

    COUNT(*) FILTER (
        WHERE clicked_product_key IS NOT NULL
    ) AS searches_with_click,

    ROUND(
        COUNT(*) FILTER (
            WHERE clicked_product_key IS NOT NULL
        )::NUMERIC
        / NULLIF(
            COUNT(*),
            0
        )
        * 100,
        2
    ) AS search_ctr,

    COUNT(*) FILTER (
        WHERE generated_purchase = TRUE
    ) AS purchases,

    ROUND(
        COUNT(*) FILTER (
            WHERE generated_purchase = TRUE
        )::NUMERIC
        / NULLIF(
            COUNT(*),
            0
        )
        * 100,
        2
    ) AS search_conversion_rate,

    COALESCE(
        SUM(revenue),
        0
    ) AS revenue

FROM analytics.fact_searches

GROUP BY search_term;

CREATE OR REPLACE VIEW analytics.vw_channel_performance AS
SELECT
    s.traffic_source,

    COUNT(DISTINCT s.session_id) AS sessions,

    COUNT(DISTINCT o.order_id) AS orders,

    COALESCE(
        SUM(o.total_amount),
        0
    ) AS revenue,

    ROUND(
        COUNT(DISTINCT o.order_id)::NUMERIC
        / NULLIF(
            COUNT(DISTINCT s.session_id),
            0
        )
        * 100,
        2
    ) AS conversion_rate,

    ROUND(
        COALESCE(
            AVG(o.total_amount),
            0
        ),
        2
    ) AS average_order_value

FROM analytics.fact_sessions s

LEFT JOIN analytics.fact_orders o
    ON s.session_id = o.session_id

GROUP BY s.traffic_source;

CREATE OR REPLACE VIEW analytics.vw_product_performance AS
SELECT
    p.product_key,
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand,
    p.price,

    COUNT(*) FILTER (
        WHERE e.event_type = 'product_view'
    ) AS product_views,

    COUNT(*) FILTER (
        WHERE e.event_type = 'add_to_cart'
    ) AS add_to_carts,

    COUNT(*) FILTER (
        WHERE e.event_type = 'purchase'
    ) AS purchases,

    ROUND(
        COUNT(*) FILTER (
            WHERE e.event_type = 'add_to_cart'
        )::NUMERIC
        / NULLIF(
            COUNT(*) FILTER (
                WHERE e.event_type = 'product_view'
            ),
            0
        )
        * 100,
        2
    ) AS add_to_cart_rate,

    ROUND(
        COUNT(*) FILTER (
            WHERE e.event_type = 'purchase'
        )::NUMERIC
        / NULLIF(
            COUNT(*) FILTER (
                WHERE e.event_type = 'product_view'
            ),
            0
        )
        * 100,
        2
    ) AS product_conversion_rate,

    COALESCE(
        SUM(
            CASE
                WHEN e.event_type = 'purchase'
                THEN oi.line_total
                ELSE 0
            END
        ),
        0
    ) AS revenue

FROM analytics.dim_product p

LEFT JOIN analytics.fact_events e
    ON p.product_key = e.product_key

LEFT JOIN analytics.fact_orders o
    ON e.session_id = o.session_id
    AND e.event_type = 'purchase'

LEFT JOIN analytics.fact_order_items oi
    ON o.order_id = oi.order_id
    AND p.product_key = oi.product_key

GROUP BY
    p.product_key,
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand,
    p.price;

    