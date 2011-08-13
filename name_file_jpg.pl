#
# Perl script to copy and rename jpg files 
# based on EXIF File Number (in jpg file), e.g. x.jpg -> IMG_1234.jpg
# also sets the file creation/modify time to EXIF Create Time
#
    use File::Find;	
    use File::Copy;
    use Time::Local;
    use Image::ExifTool;
    use Win32API::File::Time qw{:win};

    my $exifTool = new Image::ExifTool;
    $exifTool->Options(Unknown => 1);

    my $datedir = "C:/Users/scherer/Desktop/Recover";
    my @directories_to_search = ('/Users/scherer/Desktop/Recover');

    open (TXT, ">exiftools.log"); 

    find({ wanted => \&wanted},  @directories_to_search);
	
    close TXT;

    exit; 

# here is where the copy/rename/touch is done
#
    sub wanted { 
    my $file = $_;  # name of found file 
    my $from = "$File::Find::name";  # name and path 

#   $from =~ s/\//\\/g; # change / to \ in path if required
   print TXT "----------------\n$file\n$File::Find::name\n"; 
    if (/\.jpg$/i) {
       my $info = $exifTool->ImageInfo($file);
#      print TXT %$info,"\n";
       my $tag = 'FileNumber';
       my $val = $info->{$tag};
       if ($exifTool->GetDescription($tag) =~ /File Number/) {
      	  $val =~ m/(.*)-(.*)/;
          my $val = $info->{$tag};
	  my $path = $1."CANON";
	  my $name = $2;
 	  print TXT ">>$tag=$val<<\n$path/IMG_$name.jpg\n";
       	  my $tag = 'CreateDate';
          my $val = $info->{$tag};
          my @date = split(/[ :]/,$val);
          my $time = timelocal($date[5],$date[4],$date[3],
		  $date[2],$date[1]-1,$date[0]-1900);
          my $string = localtime $time;
 	  print TXT ">>$tag=$val<<\n@date\n$time\n$string\n";

          my $to = "$datedir/$path/IMG_$name.jpg";

	  mkdir "$datedir/$path" unless stat("$datedir/$path");
	  if (stat("$datedir/$path/$file")) {
		  print TXT " exists {time} $now";
		  utime ($time, $time, $to);
                  SetFileTime ($to, time, $time, $time);

          } else {
		  print TXT " copy  $from , $to ,$time, $now ";
 		  copy ($from, $to);
		  utime ($time, $time, $to);
                  SetFileTime ($to, time, $time, $time);
	  }
                  
      }
      print TXT "\n===========================\n";
      return;
   }
}
