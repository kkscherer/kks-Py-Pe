use File::Find;
my @dirs = "/users/scherer/perl";
my $i,$d,$f;

find( {
#    preprocess => sub { return grep {/jpg$/i } @_ },
#    preprocess => sub { return grep { -d | /jpg/ } @_ },
    wanted => sub { if (/\.jpg$/i) {
		    print "\n", "$i $d", "-",$f++, ".) ", $_
	    } elsif ( -d  ) {
		    $d++;
	    } else {
		    $i++;
	    }
    }, 
    }, @dirs);

