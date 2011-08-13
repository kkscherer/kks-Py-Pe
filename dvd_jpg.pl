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
    my @dvddir  = ('/Users/scherer/Desktop/Karl/DVD1');
    our $total = 0;
    our $base =  4600000000*($dvd-1) - 500000000;
    our $limit = 4600000000*$dvd;
    open( TXT, ">exiftools.log" );

    find( { wanted => \&wanted }, @datedir );

    close TXT;

    exit;

    sub wanted {
        my $file   = $_;
        my $source = "$File::Find::dir";
        print TXT "$source/$file";
        if ( $file =~ /\.lnk$/i && $file =~ /\.jpg/i ) {
            my $shcut = $wsh->CreateShortcut($_) or die;
	    my $target =  $shcut->TargetPath;
	    $target =~ s/\\/\//g;
            print TXT " - $target";
            my $destdir = $source;
            $destdir =~ s/By Date/DVD1/;
            my $dest = $destdir . "/" . $file;
	    $dest =~ s/\.lnk$//i;
            print TXT "\n", $target, " -> $dest";
            my $st = stat( $target ) or next;
            my $size = $st->size;
            $total += $size;
	    if ($total < $base ) { next }
            mkdir "$destdir" unless stat("$destdir");
	    my $cpst = copy("$target", "$dest");
            print TXT " $size,$total - $cpst";
	    if ($total > $limit) { exit }
        }
        print TXT "\n";
    }

