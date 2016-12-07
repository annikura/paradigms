select City.Name, City.Population, Country.Population
from City inner join Country
on City.CountryCode = Country.Code
order by City.Population / Country.Population desc
limit 20; 
