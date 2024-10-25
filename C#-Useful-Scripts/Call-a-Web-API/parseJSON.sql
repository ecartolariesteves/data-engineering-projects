DECLARE @JSON nvarchar(4000) =
	(SELECT TOP 1
	JSON
FROM
	[dbo].[tablaJSON]
WHERE
	Metodo = 'Metodo_REE'
ORDER BY
	FechaCarga DESC
)

INSERT INTO TableDestination
           (ColumnA
           ,ColumnB
		   ,ColumnC)

SELECT
	'A' AS ColumnA,
	cast(t1.StringValue as float) ColumnB,
	RIGHT('0' + cast(MONTH(t2.StringValue) as nvarchar(2)),2)  + '/' + cast(YEAR(t2.StringValue) as nvarchar(4)) as ColumnC
FROM
	(SELECT
		*
	FROM
		parseJSON(@JSON)
	WHERE
		Name = 'value'
	) t1
INNER JOIN
	(SELECT
		*
	FROM
		parseJSON(@JSON)
	WHERE
		Name = 'datetime'
	) t2 on t1.Parent_ID = t2.Parent_ID