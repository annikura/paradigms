select Country.Name, LiteracyRate.Rate Rate
from Country inner join LiteracyRate
on Country.Code = LiteracyRate.CountryCode
group by Country.Code
having LiteracyRate.Year = max(LiteracyRate.Year)
order by Rate desc
limit 1;
