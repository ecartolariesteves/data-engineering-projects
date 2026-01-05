-- =====================================
-- SCRIPT DE PRUEBA DE RENDIMIENTO
-- =====================================

-- Limpieza previa
IF OBJECT_ID('tempdb..#TestPerformance') IS NOT NULL
    DROP TABLE #TestPerformance;

PRINT '=== Iniciando prueba de rendimiento ===';
DECLARE @StartTime DATETIME = GETDATE();

-- =====================================
-- 1. Crear tabla temporal con muchos datos
-- =====================================
CREATE TABLE #TestPerformance (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Nombre NVARCHAR(100),
    Categoria NVARCHAR(50),
    Valor DECIMAL(18,2),
    Fecha DATETIME
);

PRINT 'Insertando datos...';
DECLARE @i INT = 0;
WHILE @i < 1000000  -- 1 millón de registros (ajusta si quieres más o menos carga)
BEGIN
    INSERT INTO #TestPerformance (Nombre, Categoria, Valor, Fecha)
    VALUES (
        CONCAT('Producto-', @i),
        CASE WHEN @i % 5 = 0 THEN 'A'
             WHEN @i % 5 = 1 THEN 'B'
             WHEN @i % 5 = 2 THEN 'C'
             WHEN @i % 5 = 3 THEN 'D'
             ELSE 'E' END,
        RAND() * 1000,
        DATEADD(DAY, -@i % 365, GETDATE())
    );
    SET @i += 1;
END;

PRINT 'Datos insertados. Ejecutando consultas pesadas...';

-- =====================================
-- 2. Pruebas de rendimiento
-- =====================================

-- Consulta 1: Agregación
DECLARE @AggStart DATETIME = GETDATE();
SELECT Categoria, COUNT(*) AS Total, AVG(Valor) AS Promedio
FROM #TestPerformance
GROUP BY Categoria;
PRINT 'Consulta 1 completada en ' + CAST(DATEDIFF(MILLISECOND, @AggStart, GETDATE()) AS NVARCHAR(20)) + ' ms';

-- Consulta 2: Ordenamiento
DECLARE @SortStart DATETIME = GETDATE();
SELECT TOP 1000 * 
FROM #TestPerformance
ORDER BY Valor DESC;
PRINT 'Consulta 2 completada en ' + CAST(DATEDIFF(MILLISECOND, @SortStart, GETDATE()) AS NVARCHAR(20)) + ' ms';

-- Consulta 3: Filtro complejo
DECLARE @FilterStart DATETIME = GETDATE();
SELECT *
FROM #TestPerformance
WHERE Categoria = 'C' AND Valor BETWEEN 100 AND 900
ORDER BY Fecha DESC;
PRINT 'Consulta 3 completada en ' + CAST(DATEDIFF(MILLISECOND, @FilterStart, GETDATE()) AS NVARCHAR(20)) + ' ms';

-- =====================================
-- 3. Fin de la prueba
-- =====================================
PRINT '=== Prueba completada ===';
PRINT 'Tiempo total: ' + CAST(DATEDIFF(SECOND, @StartTime, GETDATE()) AS NVARCHAR(20)) + ' segundos';

-- Limpieza final (opcional)
-- DROP TABLE #TestPerformance;
