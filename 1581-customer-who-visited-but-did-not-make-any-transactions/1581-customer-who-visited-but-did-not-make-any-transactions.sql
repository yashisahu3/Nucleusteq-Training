# Write your MySQL query statement below
SELECT customer_id,count(customer_id) as count_no_trans
FROM Visits left join Transactions
on Visits.visit_id=Transactions.visit_id
where transaction_id is null
group by customer_id;