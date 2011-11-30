# Goes thru the By Date directory tree with links (shortcuts) to images.
# picks out all jpg image links and copies the originals into the DVD tree.
# uses the $dvd index to split the total into DVD size 'bites'
# kks 20091215

    use File::Find;
    use File::Copy;
    use File::stat;

    use Win32::OLE;
    my $wsh = new Win32::OLE 'WScript.Shell';
    my $dvd =  $ARGV[0] ? $ARGV[0] :1;

    my @datedir = "C:/Users/scherer/Desktop/Karl/By Date";
    my $dvddir  = "C:/Users/scherer/Desktop/Karl/DVD$dvd";
    our $total = 0;
    our $base =  4600000000*($dvd-1); # not sure why -> - 500000000;
    our $limit = $base + 4600000000;
    our $limit = $base + 14600000;

    open( TXT, ">exiftools.log" );

    mkdir "$dvddir" unless stat("$dvddir");
    print TXT "--> $dvddir\n";

    find( { wanted => \&wanted }, @datedir );

    close TXT;


    exit;

    sub wanted {
        my $file   = $_;
        my $source = "$File::Find::dir";
        print TXT "$source/$file\n";
        if ( $file =~ /\.lnk$/i && $file =~ /\.jpg/i ) {
            my $shcut = $wsh->CreateShortcut($_) or die;
	    my $target =  $shcut->TargetPath;
	    $target =~ s/\\/\//g;
            my $st = stat( $target ) or next;
            print TXT " >- $target\n";
# TODO           
	    my $destdir = $source;
            $destdir =~ s/.*By Date/$dvddir/;
            my $dest = $destdir . "/" . $file;
	    $dest =~ s/\.lnk$//i;
# TODO /
            my $size = $st->size;
            $total += $size;
	    if ($total < $base ) { next }
            mkdir "$destdir" unless stat("$destdir");
	    my $cpst = copy("$target", "$dest");
	    print TXT  " -> $dest -- $size,$total, ($cpst)";
	    if ($total > $limit) { exit }
        }
        print TXT "\n";
    }

