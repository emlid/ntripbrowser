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

VALID_NTRIP_TRIM_DISTANCE = b'SOURCETABLE 200 OK \n' \
                            b'STR;near;Rehakka;RTCM 3.3;1004(1),1005(10),1008(10),1012(1),1019(3),1020(2),1033(10),1042(3),1046(1),1077(1),1087(1),1097(1),1127(1),1230(30);2;GPS+GLO+GAL+BDS;SNIP;FIN;1.1;2.2;1;0;sNTRIP;none;B;N;12220;\n' \
                            b'STR;far;Drummond;RTCM 3.2;1005(10),1074(1),1084(1),1094(1),1124(1),1230(1);2;GPS+GLO+GAL+BDS;SNIP;BRA;10.1;20.2;1;0;sNTRIP;none;B;N;7300;\n' \
                            b'ENDSOURCETABLE'
