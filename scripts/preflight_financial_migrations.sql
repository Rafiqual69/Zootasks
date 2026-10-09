-- Read-only preflight for the financial constraints introduced by the
-- security branch. Returns only check names and violation counts; no user data.
SELECT 'tasks.negative_reward' AS check_name, COUNT(*)::bigint AS violations
FROM tasks_task WHERE reward < 0
UNION ALL
SELECT 'tasks.completed_workers_gt_max', COUNT(*)::bigint
FROM tasks_task WHERE completed_workers > max_workers
UNION ALL
SELECT 'tasks.active_claims_gt_max', COUNT(*)::bigint
FROM tasks_task t
WHERE (
    SELECT COUNT(*)
    FROM tasks_taskclaim c
    WHERE c.task_id = t.id AND c.status <> 'rejected'
) > t.max_workers
UNION ALL
SELECT 'promotions.negative_reward', COUNT(*)::bigint
FROM promotions_promotion WHERE reward < 0
UNION ALL
SELECT 'promotions.negative_budget', COUNT(*)::bigint
FROM promotions_promotion WHERE budget < 0
UNION ALL
SELECT 'promotions.completed_workers_gt_max', COUNT(*)::bigint
FROM promotions_promotion WHERE completed_workers > max_workers
UNION ALL
SELECT 'promotions.active_claims_gt_max', COUNT(*)::bigint
FROM promotions_promotion p
WHERE (
    SELECT COUNT(*)
    FROM promotions_promotionclaim c
    WHERE c.promotion_id = p.id AND c.status <> 'rejected'
) > p.max_workers
UNION ALL
SELECT 'accounts.negative_wallet_fields', COUNT(*)::bigint
FROM accounts_workerprofile
WHERE balance < 0 OR reserved_balance < 0 OR total_earned < 0
UNION ALL
SELECT 'accounts.reserved_balance_gt_balance', COUNT(*)::bigint
FROM accounts_workerprofile WHERE reserved_balance > balance
UNION ALL
SELECT 'wallet.negative_withdrawal_amount', COUNT(*)::bigint
FROM wallet_withdrawalrequest WHERE amount < 0
UNION ALL
SELECT 'wallet.task_identity_type_mismatch', COUNT(*)::bigint
FROM wallet_wallettransaction
WHERE task_claim_id IS NOT NULL AND transaction_type <> 'earning'
UNION ALL
SELECT 'wallet.promotion_identity_type_mismatch', COUNT(*)::bigint
FROM wallet_wallettransaction
WHERE promotion_claim_id IS NOT NULL AND transaction_type <> 'earning'
UNION ALL
SELECT 'wallet.withdrawal_identity_type_mismatch', COUNT(*)::bigint
FROM wallet_wallettransaction
WHERE withdrawal_id IS NOT NULL AND transaction_type <> 'withdrawal'
UNION ALL
SELECT 'wallet.multiple_operation_identities', COUNT(*)::bigint
FROM wallet_wallettransaction
WHERE (task_claim_id IS NOT NULL)::int
    + (promotion_claim_id IS NOT NULL)::int
    + (withdrawal_id IS NOT NULL)::int > 1
ORDER BY check_name;
