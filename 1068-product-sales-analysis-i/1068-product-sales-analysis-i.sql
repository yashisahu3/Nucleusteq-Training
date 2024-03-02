# Write your MySQL query statement below
SELECT  product_name,year,price
FROM Sales join Product
on Sales.product_id=Product.product_id
order by sale_id;
