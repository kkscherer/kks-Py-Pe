    #########
    use Cwd;
    my $dir = cwd;

    use Win32::OLE;
    my $wsh = new Win32::OLE 'WScript.Shell';

    open (TXT, ">exiftools.log");

    #####################

    use Image::ExifTool;
    my $exifTool = new Image::ExifTool;
    $exifTool->Options(Unknown => 1);

    opendir CWD, ".";
    my @jpegs = grep {/jpg$/i} readdir(CWD);
    closedir DIR;
    print @jpegs;

    my $file;
foreach $file (@jpegs) {
    my $info = $exifTool->ImageInfo($file);
    my $group = '';
    my $tag;


    foreach $tag ($exifTool->GetFoundTags('Group0')) {
        if ($group ne $exifTool->GetGroup($tag)) {
            $group = $exifTool->GetGroup($tag);
            print  "---- $group ----\n";
        }
        my $val = $info->{$tag};
        if (ref $val eq 'SCALAR') {
            if ($$val =~ /^Binary data/) {
                $val = "($$val)";
            } else {
                my $len = length($$val);
                $val = "(Binary data $len bytes)";
            }
        }
	if ($exifTool->GetDescription($tag) =~ /Date.Time Original/) {
		$val =~ s/(.*) (.*)/$1/;
		$val =~ s/:/-/g;
		mkdir $val;
    my $shcut = $wsh->CreateShortcut("./$val/$file.lnk") or
   			 die("./$val/$file.lnk");
    $shcut->{'TargetPath'} = "$dir/$file";
    my $comment = "moved from $dir/$file";
    $shcut->{'Description'} = $comment if defined $comment;
    $shcut->Save;

#      		symlink("a.jpg","$val/a.jpg");
		printf TXT ("%-32s : %s\n", $exifTool->GetDescription($tag), $val);
        }
}
}
close TXT;
exit;
