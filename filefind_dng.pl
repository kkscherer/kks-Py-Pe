# search a directory tree for non jpg image/video files and create shortcuts in # date indexed directory tree 
    use File::Find;

    use Win32::Shortcut;
    my $LINK = new Win32::Shortcut();

    use Image::ExifTool;
    my $exifTool = new Image::ExifTool;
    $exifTool->Options(Unknown => 1);

    my $datedir = "C:/Users/scherer/Desktop/Karl/Non JPG";
    my @directories_to_search = ('/Users/scherer/Desktop');

    open (TXT, ">exiftools.log");

    find({ wanted => \&wanted},  @directories_to_search);
	
    close TXT;
    $LINK->Close();
    

    exit; 

    sub wanted {
    my $file = $_;
    my $target = "$File::Find::name";
    $target =~ s/\//\\/g;
    print TXT "\n$File::Find::name"; 
    if (/\.dng$|\.crw$|\.psd$|\.png$|\.tiff?$\.mov$|\.mp.+$|\.avi$/i) {
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
 		$LINK->Load("$datedir/$val/$file.lnk");
    		my $trgt = $LINK->{'Path'};
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
           $LINK->{'File'} = "$datedir/$val/$file.lnk";
	   $LINK->{'Path'} = $target;
           my $comment = time;
	   $LINK->{'Description'} = $comment if defined $comment;
	   $LINK->Save();
	   print TXT "\n     - $datedir/$val/$file.lnk";
#	printf ("%-32s : %s\n", $val, $file);
      }
      print TXT "\n";
      return;
   }
}
