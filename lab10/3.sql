select City.Name from 
(Country inner join Capital 
on Country.Code = Capital.CountryCode) 
inner join City
on Country.Code = City.CountryCode and City.Id = Capital.CityId
where Country.Name = 'Malaysia';
 
