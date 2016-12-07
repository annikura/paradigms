select GovernmentForm, sum(SurfaceArea) Surface
from Country
group by GovernmentForm
order by Surface desc
limit 1;
