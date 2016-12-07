select Country.Name, Country.Population, sum(City.Population)
from Country inner join City
on Country.Code = City.CountryCode
group by Country.Code
having Country.Population > sum(City.Population) * 2
order by Country.Name;
