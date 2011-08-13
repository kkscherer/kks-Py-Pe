    use File::Find;

    use Win32::OLE;
    my $wsh = new Win32::OLE 'WScript.Shell';

    use Image::ExifTool;
    my $exifTool = new Image::ExifTool;
    $exifTool->Options(Unknown => 1);

    my $datedir = "C:/Users/scherer/Desktop/Karl_By_Date";
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
    if (/\.jpg$/i) {
       my $info = $exifTool->ImageInfo($file);
       my $tag = 'CreateDate';
       my $val = $info->{$tag};
       if ($exifTool->GetDescription($tag) =~ /Create Date/) {
      	  $val =~ s/(.*) (.*)/$1/;
	  $val =~ s/:/-/g;
	  mkdir "$datedir/$val" unless stat("$datedir/$val");
	  my $i;
	  while (stat("$datedir/$val/$file.lnk")) {
		  print TXT " exists ";
 		$shcut = $wsh->CreateShortcut("$datedir/$val/$file.lnk") or die;
    		my $trgt = $shcut->TargetPath;
		print TXT "\n$trgt\nC:$target\n";
		if ($trgt eq "C:$target") {print TXT " same trgt ";last}
		print TXT " diff trgt $i";
		print "\++++++++++++++++++++++++++++++++\n";
		if ($file =~ /\((\d+\))\./) {
			$i = $1; $i++;
			$file =~ s/\(\d+\)\./($i)./;
		} else {
			$file =~ s/\./(1)./;
		}
	   }
           $shcut = $wsh->CreateShortcut("$datedir/$val/$file.lnk") or
   			 die("$datedir/$val/$file.lnk");
           $shcut->{'TargetPath'} = $target;
           my $comment = time;
           $shcut->{'Description'} = $comment if defined $comment;
           $shcut->Save;
	   print TXT "\n     - $datedir/$val/$file.lnk";
#	printf ("%-32s : %s\n", $val, $file);
      }
      print TXT "\n";
      return;
   }
}
