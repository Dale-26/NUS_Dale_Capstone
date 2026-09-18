let
    Source = Csv.Document(File.Contents(DataFile),[Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers,{{"holiday", type text},{"temp", type number},{"rain_1h", type number},{"snow_1h", type number},{"clouds_all", Int64.Type},{"weather_main", type text},{"weather_description", type text},{"date_time", type datetime},{"traffic_volume", Int64.Type}},"en-US"),
    AddHour = Table.AddColumn(Typed,"Hour",each Time.Hour(DateTime.Time([date_time])),Int64.Type),
    AddDate = Table.AddColumn(AddHour,"Date",each Date.From([date_time]),type date),
    AddYear = Table.AddColumn(AddDate,"Year",each Date.Year([date_time]),Int64.Type),
    AddCelsius = Table.AddColumn(AddYear,"Temperature Celsius",each if [temp] < 200 or [temp] > 330 then null else [temp]-273.15,type number),
    Category = Table.AddColumn(AddCelsius,"Traffic Category",each if [traffic_volume]<4500 then "Low" else if [traffic_volume]<=5500 then "Medium" else "High",type text)
in
    Category