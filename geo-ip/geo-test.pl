  use Geo::IP;

  my $name = "kks.ddns.net";
  
  my $gi = Geo::IP->new(GEOIP_STANDARD);
  # look up IP address '24.24.24.24'
  # returns undef if country is unallocated, or not defined in our database
  # my $country = $gi->country_code_by_addr('24.24.24.24');
  $country = $gi->country_code_by_name($name);
  $cname = $gi->country_name_by_name($name);
  # $country is equal to "US"
  print "result: $country - $cname \n";

  $gi = Geo::IP->open("/GeoIP/GeoLiteCity.dat", GEOIP_STANDARD);
  my $record = $gi->record_by_name($name);
# my $record = $gi->record_by_addr('71.141.102.40');
  print $record->country_code,"\n",
        $record->country_code3,"\n",
        $record->country_name,"\n",
        $record->region,"\n",
        $record->region_name,"\n",
        $record->city,"\n",
        $record->postal_code,"\n",
        $record->latitude,"\n",
        $record->longitude,"\n",
        $record->time_zone,"\n",
        $record->area_code,"\n",
    $record->continent_code,"\n",
        $record->metro_code,"\n";
