# Use this script to go thru a directory (and subdirs) of pictures and
# create a set of directories named yyyy-mm-dd with shortcuts to the image
# files that where _taken_ on this date.
#
    use File::Find;	# needed to find files in dir tree

    use Win32::OLE;	# needed to create MS shortcuts
    my $wsh = new Win32::OLE 'WScript.Shell';

    use Image::ExifTool;	# gets info out of jpg image files
    my $exifTool = new Image::ExifTool;
    $exifTool->Options(Unknown => 1);

# create date dirs with shortcuts here:    
    my $datedir = "C:/Users/scherer/Desktop/Karl_By_Date";
# search this (these) directories and subdirs
    my @directories_to_search = ('/Users/scherer/Desktop/Karl');

# open log file
    open (TXT, ">exiftools.log");

# walk directories and call code
    find({ wanted => \&wanted},  @directories_to_search);
	
    close TXT;

    exit; 

# this is where each found file is checked
    sub wanted {
    my $file = $_;	# passed in current path/file name (eq: $File::Find::name)
    my $shcut;		
    print TXT "\n$File::Find::name"; 
    my $target = "$File::Find::name";
    $target =~ s/\//\\/g;
    if (/\.jpg$/i) { # only deal with jpg files
       my $info = $exifTool->ImageInfo($file);
       my $tag = 'CreateDate';
       my $val = $info->{$tag};	# get the date picture was taken
       if ($exifTool->GetDescription($tag) =~ /Create Date/) { # if date exists
      	  $val =~ s/(.*) (.*)/$1/;	# get the date portion 
	  $val =~ s/:/-/g;		# replace : (can't be in dir name)
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
	   }	# check if shortcut exists and has different target
	   	# if so, create new shortcut with incremented number in name
           $shcut = $wsh->CreateShortcut("$datedir/$val/$file.lnk") or
   			 die("$datedir/$val/$file.lnk");
           $shcut->{'TargetPath'} = $target;
           my $comment = time; # put current time in comments - ???
           $shcut->{'Description'} = $comment if defined $comment;
           $shcut->Save;
	   print TXT "\n   - $datedir/$val/$file.lnk";
#	printf ("%-32s : %s\n", $val, $file);
      }
      print TXT "\n";
      return;
   }
}
