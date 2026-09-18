# Power BI project

Open `Traffic.pbip` in Power BI Desktop on Windows. Change the DataFile Power Query parameter to the full path of the supplied raw CSV, then Refresh. The project includes two report pages, three KPI cards, daily and hourly trend charts, weather comparison, scatter plot and slicers. Use the Hour slicer in Between mode for an hour range. Save as PBIX after validating the report.

Status: Generated PBIP/PBIR and semantic model source; desktop rendering and refresh have not been verified in this macOS environment. This is not a verified PBIX deliverable. Before submission, verify all charts and slicer interactions in Desktop and include the resulting PBIX or validated project.

Raw record weighting is retained for task comparability. Total Hours uses DISTINCTCOUNT and therefore does not mislabel 48,204 weather records as distinct hours. Invalid temperatures are excluded only from the Celsius KPI; the raw scatter retains 0 K readings to expose outliers. Data has 48,204 rows, 9 original columns, no blank fields; holiday None is a valid non-holiday marker, not missing data. The Python model uses a separate cleaned hourly table.

Microsoft format documentation: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
