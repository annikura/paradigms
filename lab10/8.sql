select Country.Name, Country.Population, Country.SurfaceArea
from Country, City C1, Capital, City C2
on Capital.CountryCode = C2.CountryCode and Capital.CityId = C2.Id and
   Country.Code = Capital.CountryCode and C1.CountryCode = Country.Code and
   C2.Population < C1.Population
group by Country.Name, Country.Population, Country.SurfaceArea
order by 1.0 * Country.Population / Country.SurfaceArea, Country.Name;
	

