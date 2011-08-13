    use File::Find;
    use File::Copy;

    use Image::ExifTool;
    my $exifTool = new Image::ExifTool;
    $exifTool->Options(Unknown => 1);

    my $datedir = "C:/Users/scherer/Desktop/Karl/by dvd";
    my @directories_to_search = ('/Users/scherer/Desktop/Karl');

    open (TXT, ">exiftools.log");

    find({ wanted => \&wanted},  @directories_to_search);
	
    close TXT;

    exit; 

    sub wanted {
    my $file = $_;
    my $shcut;
    my $target = "$File::Find::name";
    $target =~ s/\//\\/g;
    print TXT "$File::Find::name"; 
    if ($File::Find::name =~ /by /i) {
        print TXT " - skip";
    } else {
	if (/\.jpg$/i) {
       		my $info = $exifTool->ImageInfo($file);
       		my $tag = 'CreateDate';
       		my $val = $info->{$tag};
       		if ($exifTool->GetDescription($tag) =~ /Create Date/) {
        		$val =~ s/(.*) (.*)/$1/;
	  		$val =~ s/:/-/g;
	  		mkdir "$datedir/$val" unless stat("$datedir/$val");
	  		if (stat("$datedir/$val/$file.lnk")) {
				print TXT " exists ";
	  		} else {
				my $cpst = copy($target, "$datedir/$val/$file");
				print TXT " - $val,$cpst"; 
	   		}
#	   print TXT "\n     - $datedir/$val/$file.lnk";
#	printf ("%-32s : %s\n", $val, $file);
      		}
	}
   }
      print TXT "\n";
      return;
}
