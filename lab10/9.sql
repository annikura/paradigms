select B.Year, E.Year, Country.Name, 1.0 * (E.Rate - B.Rate) / (E.Year - B.Year)
MidInc
from Country, LiteracyRate B, LiteracyRate E
on Country.Code = B.CountryCode and Country.Code = E.CountryCode and B.Year < E.Year
group by Country.Name, B.Year
having E.Year = min(E.Year)
order by MidInc desc;
