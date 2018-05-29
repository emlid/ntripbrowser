VALID_NET_NTRIP = b'SOURCETABLE 200 OK \n' \
                  b'NET;Str1;Str2;B;N;https://example.htm;http://example.htm;http://sample;none\n' \
                  b'ENDSOURCETABLE'

VALID_STR_NTRIP = b'SOURCETABLE 200 OK \n' \
                  b'STR;Str3;Str4;B;N;https://example2.htm;http://example2.htm;http://sample2;none\n' \
                  b'ENDSOURCETABLE'

VALID_CAS_NTRIP = b'SOURCETABLE 200 OK \n' \
                  b'CAS;example;2101;NtripCaster;None;0;Null;11;22.33;1.2.3.4;5;http://sample.htm\n' \
                  b'ENDSOURCETABLE'

VALID_NTRIP = b'SOURCETABLE 200 OK \n' \
              b'CAS;example;2101;NtripCaster;None;0;Null;11;22.33;1.2.3.4;5;http://sample.htm\n' \
              b'STR;Str3;Str4;B;N;https://example2.htm;http://example2.htm;http://sample2;none\n' \
              b'NET;Str1;Str2;B;N;https://example.htm;http://example.htm;http://sample;none\n' \
              b'ENDSOURCETABLE'
