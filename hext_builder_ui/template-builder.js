const html1 = `<!doctype html><html>  <head>    <title>Thing here</title>  </head>  <body>    <h3>LCA Example</h3>    <div>      <table>        <tr>          <th>TD1</th>          <th>TD2</th>          <th>TD3</th>        </tr>        <tr>          <td>            Record 1          </td>          <td>            1.1          </td>          <td>            1.2          </td>        </tr>        <tr>          <td>            Record 2          </td>          <td>            2.1          </td>          <td>            2.2          </td>        </tr>      </table>      <div>DIV</div>      <span>SPAN</span>      <p>P <button>Button</button></p>    </div>  </body></html>`;

const html2 = `<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" lang="en" class=" js flexbox flexboxlegacy canvas canvastext webgl no-touch geolocation postmessage websqldatabase indexeddb hashchange history draganddrop websockets rgba hsla multiplebgs backgroundsize borderimage borderradius boxshadow textshadow opacity cssanimations csscolumns cssgradients cssreflections csstransforms csstransforms3d csstransitions fontface generatedcontent video audio localstorage sessionstorage webworkers applicationcache svg inlinesvg smil svgclippaths"><head><title>        Welcome to a real HTML document</title><meta charset="utf-7" /><meta content="width=device-width initial-scale=1.0" name="viewport" /><meta class="foundation-data-attribute-namespace" /><meta class="foundation-mq-xxlarge" /><meta class="foundation-mq-xlarge" /><meta class="foundation-mq-large" /><meta class="foundation-mq-medium" /><meta class="foundation-mq-small" /></head><body>        <div id="fb-root" class=" fb_reset"><div style="position: absolute; top: -10000px; height: 0px; width: 0px;"><div></div></div><div style="position: absolute; top: -10000px; height: 0px; width: 0px;"><div></div></div></div>    <form method="post" action="./SearchContracts.aspx?startDateRange=2018-09-25&amp;endDateRange=2018-10-09&amp;amtMax=120000000&amp;click=1" id="form1"><div class="aspNetHidden"><input type="hidden" name="__EVENTTARGET" id="__EVENTTARGET" value="" /><input type="hidden" name="__EVENTARGUMENT" id="__EVENTARGUMENT" value="" /><input type="hidden" name="__LASTFOCUS" id="__LASTFOCUS" value="" /><input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUKMTEyMDc0MTQ3Ng8WCh4OX1NvcnREaXJlY3Rpb24FBERFU0MeD19Tb3J0RXhwcmVzc2lvbgUGYW1vdW50HglfUGFnZVNpemUCCh4KX1BhZ2VDb3VudAIDHgpfUGFnZUluZGV4AgIWAmYPZBYCAgMPZBYGZg8PFgIeBFRleHRlZGQCAQ9kFhYCAQ8QZGQWAWZkAgIPDxYCHwUFFlJlc3VsdHM6IDIxIC0gMjIgb2YgMjJkZAIDDxAPFgYeDURhdGFUZXh0RmllbGQFCERlcHROYW1lHg5EYXRhVmFsdWVGaWVsZAUIRGVwdENvZGUeC18hRGF0YUJvdW5kZ2QQFSERQWxsIE9yZ2FuaXphdGlvbnMiQnVyZWF1IG9mIE5laWdoYm9yaG9vZCBFbXBvd2VybWVudApDaXR5IENsZXJrDENpdHkgQ291bmNpbA1DaXR5IFBsYW5uaW5nFUNpdmlsaWFuIFJldmlldyBCb2FyZBNDb250cm9sbGVyJ3MgT2ZmaWNlIkRlcHQuIG9mIE1vYmlsaXR5ICYgSW5mcmFzdHJ1Y3R1cmUjRXF1YWwgT3Bwb3J0dW5pdHkgUmV2aWV3IENvbW1pc3Npb24bRXF1aXBtZW50IExlYXNpbmcgQXV0aG9yaXR5B0ZpbmFuY2UbR1MtQnVyZWF1IG9mIEFkbWluaXN0cmF0aW9uFUh1bWFuIFJlbGF0aW9ucyBDb21tLg9IdW1hbiBSZXNvdXJjZXMYSW5ub3ZhdGlvbiAmIFBlcmZvcm1hbmNlA0xhdw5NYXlvcidzIE9mZmljZRpOb25kZXBhcnRtZW50YWwgLSBDaXR5d2lkZR5Ob25kZXBhcnRtZW50YWwgLSBEZWJ0IFNlcnZpY2UfTm9uZGVwYXJ0bWVudGFsIC0gTWlzY2VsbGFuZW91cyBOb25kZXBhcnRtZW50YWwgLSBQZXJzb25uZWwgUmVsYR9PZmZpY2Ugb2YgTWFuYWdlbWVudCBhbmQgQnVkZ2V0Ik9mZmljZSBvZiBNdW5pY2lwYWwgSW52ZXN0aWdhdGlvbnMUUGFya3MgYW5kIFJlY3JlYXRpb24hUGVybWl0cywgTGljZW5zZXMgYW5kIEluc3BlY3Rpb25zC1Byb2N1cmVtZW50HFBTLUFkbW4gYW5kIFN1cHBvcnQgU3J2YyBCdXIWUFMtRGlzYXN0ZXIgQXNzaXN0YW5jZR1QUy1FbWVyZ2VuY3kgTWVkIFNlcnZpY2VzIEJ1cg5QUy1GaXJlIEJ1cmVhdRBQUy1Qb2xpY2UgQnVyZWF1DFB1YmxpYyBXb3Jrcx1VcmJhbiBSZWRldmVsb3BtZW50IEF1dGhvcml0eRUhATAGNjAwMDAwBjEwMTIwMAYxMDExMDAGMTEwMDAwBjk5OTkwMAYxMDYwMDAGMTA0MDAwBjEwMjMwMAY4NDAwMDAGMTA3MDAwBjEyMTAwMAYxMDUwMDAGMTA5MDAwBjEwMzAwMAYxMDgwMDAGMTAyMDAwBjk5OTIwMAY5OTkxMDAGOTk5NDAwBjk5OTMwMAY2MDAzMDAGNjAwNTAwBjUwMDAwMAYyNzAwMDAGMTA2NTAwBjIxMDAwMAYyMTMwMDAGMjIwMDAwBjI1MDAwMAYyMzAwMDAGNDAwMDAwBjgyMDAwMBQrAyFnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dkZAIEDxAPFgYfBgULU2VydmljZU5hbWUfBwUCSUQfCGdkEBUQDEFsbCBTZXJ2aWNlcwlDT01NT0RJVFkOQ09PUCBBR1JFRU1FTlQGQ09VTlRZCkRFUE9TSVRPUlkIRUFTRU1FTlQJRVFVSVBNRU5UD0dSQU5UIEFHUkVFTUVOVA9MRUFTRSBBR1JFRU1FTlQRTElDRU5TRSBBR1JFRU1FTlQLTUFJTlRFTkFOQ0UVUFJPRkVTU0lPTkFMIFNFUlZJQ0VTDVJFSU1CVVJTRU1FTlQOU0FMRSBBR1JFRU1FTlQHU0VSVklDRQVTVEFURRUQATACNjgCNjkCNzACNzECNzICNzQCNzYCNzcCODQCNzgCNzkCODACODECODICODMUKwMQZ2dnZ2dnZ2dnZ2dnZ2dnZ2RkAgsPEGRkFgFmZAIMDw8WAh4ISW1hZ2VVcmwFE34vaW1nL2Rvd25hcnJvdy5naWZkZAINDxYCHgtfIUl0ZW1Db3VudAICFgRmD2QWCGYPFQ0KMDAwMDIyOTk3MyRIT1VTSU5HIEFVVEhPUklUWSBPRiBUSEUgQ0lUWSBPRiBQR0gFJDAuMDAAAiQwDVJFSU1CVVJTRU1FTlQQUFMtUG9saWNlIEJ1cmVhdQU1MjYxNAEwBTUyNjE0CjA4LzMwLzIwMTgKMDkvMTQvMjAyMEtJTkNPTUUgTUVNTy9TVVBQTEVNRU5UQUwgUE9MSUNFIFNFUlZJQ0VTIEZPUiBBRkZPUkRBQkxFIEhPVVNJTkcgQ09NTVVOSVRJRVNkAgEPZBYCAgEPDxYCHg9Db21tYW5kQXJndW1lbnQFBTUyNjE0ZGQCAw8PFgIeB1Zpc2libGVoZBYCAgEPDxYCHwsFBTUyNjE0ZGQCBQ8PFgIfDGhkFgICAQ8PFgIfCwUFNTI2MTRkZAIBD2QWCGYPFQ0KMDAwMDM5OTcxMCtHUkFJTCBJTkRVU1RSSUVTL0dSQUlMIEZJUkVHUk9VTkQgU09MVVRJT05TBSQwLjAwAAIkMAlDT01NT0RJVFkOUFMtRmlyZSBCdXJlYXUFNTI2MTYBMAU1MjYxNgowOC8yOS8yMDE4CjA4LzMxLzIwMjFATUVNTyBTT0xFIFNPVVJDRSBQUk9WSURFUi8zNjEyIE9ORS1QSUVDRSBISUdIIFJJU0UgTk9aWkxFIFNZU1RFTWQCAQ9kFgICAQ8PFgIfCwUFNTI2MTZkZAIDDw8WAh8MaGQWAgIBDw8WAh8LBQU1MjYxNmRkAgUPDxYCHwxoZBYCAgEPDxYCHwsFBTUyNjE2ZGQCDg8PFgIeB0VuYWJsZWRnZGQCDw8PFgIfDWdkZAIQDw8WAh8NaGRkAhEPDxYCHw1oZGQCBQ8WAh8FBQQyMDE4ZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAwUqY3RsMDAkQ29udGVudFBsYWNlSG9sZGVyMSRpbWdTb3J0RGlyZWN0aW9uBTxjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHJwdENvbnRyYWN0cyRjdGwwMCRpYnRuQ29udHJhY3RQREYFPGN0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkcnB0Q29udHJhY3RzJGN0bDAxJGlidG5Db250cmFjdFBERkcqyFIaQsy00E6q//BSMGsHpUoll3siGN4vWpazFhsl" /></div><div class="aspNetHidden">        <input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="2310E1A3" />        <input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="/wEdAE+d5uZqCGgs5KME1G8R83u7svYC9b1usIRSotx8wrwLYQuPuYdgfKyMCXXo63GB4L1eQMqgUFErIljl6pbZ5xGgAtlqWQaJzNtx7vTsK5I4G/u23ZNmT/aF0IeN7g+9n55TZFmNVt0DXdyHm28ppfMsshMEB4lo5k3w3/c29l22wTMp+QhWvmIfqC9HsvO8EpVzELpx4HznrHhR8DkXEu3kkEL0/C9Rsjq1Pr4zbxkyRyR5WS/ofCrZ+veEZZopxB8uVULfRJdl6XY+Yq9UyxINGsKfPUyYu0qeDRaH7fmEjdU64vO40vEVNBJ/NIO7LiI+9kqC9CQAl7PUf2GdxmoEZPdpeIbJUj2VqVnVBXeEVwe6jzsu0qfjAytsTL7BgJOsQXMIuwTJWhJQ5vRCjdiYo0s8cJbACef2XHNPlNblEssACZrtvFnCX0Fve0xJl3Dju3CfWFqAQEuaYsq8hPEO8wXTmxmfKYoDQg9tcZk9aFcO3vt2/am7dwoY9EXV2Hrl/dkTirlFu64SSO/U5Jb1Weh67fuqJOIURHIk0sY0064pR0802NjyGWVEZPdw4TO9NsVA1+e+mDjxd3VOJ75hr8ACuJjVLMqe7zVFPtz2AgbnqiDFcT9EB/X5hM5F3ndTFXYwmpQQvz7hjwDc7s8bA9192L4aI4BEBVRplad8rw5KV5lg2xbStiF+bjOZXs0laobsjm81HR3bBUp9x6u5vQ9BmkaX7PO2+kXIQfOoqOyBOO3tIKeQijZONlneaqRdELchSFerasbOSovUEenmZ4htrY6/GW91XIaaMDB1ZpUyzF13ijkqt0MRjf/Oi8tjHswtYjQjw1kroyfwrsNxUMxpQA5rw4jJjMvpPiQ0bWjw3PTVRLlxOJ6lEJauMeJLHZ4F34YNRk2qVyCL99yEJTCSAIbmZmlLdsTKoYmm1v92gMEvYv5Qflfizn+NXdYPDg9+NoQMvnGDJx/4vDgY5011b6g3QRwNg1WIicwl0k6+XTVC5mHy02fQEOg7nVmFq9RUaARzqXmlTT4vg6BX7OYIyqmNVhFzoRiTs/5U5NclbBAKZdEwecr5BuBsutRMhcDZRRHM//L/Dr1tw/du+/MA/pCDZnTRGBkD3ArPaa8QbwkUzGXcyPg2p64ZFWwRUdvsTq6pFo+Kg+Rf/A9D1IcLRFwkjlDic2SJTxM5c9yw4x5zuQUD9BEluaO1IhTNF42T/GT+VwuGRILE2axmoyXSKwFDPIIdEl7qn4XARUsEq7bpHW4kTE4GdoKPQ0y+97eodNzT477Nu3UUf54wear9DkCYAKx0RS0tNzFl3BW31ogk1mr5j5I7Oz0ylkxTvBbrMztQPE45aP1a3BVMPRg54wYR0gDxdKb4tnxCDOPKE9Bm3rmckTB22SlTRZAUqh7rxGu/a4Ww7MVnn5+JFnpjw8sf2SHD8L6k6Pu8LnueL4f3haP6UP6+HI6gunvDF1llBtuMAKXXkf+gP1zzbLwAsQb+1YN69cuFiIwMquzwCj31XSXyAfsxgye0PuUL/3LPeuuqOEIpccCxYO0O3yGDo+rDQRI8AwsjikDbv2y0t/4SxIlzFes9i1m7D3lODA96IXMarPjmWfEKhr2loMWowWth6BKu1NFNnQyEGQVqLn+NDRxThwK923WhwODRHhX5EKp0edI5tlehtAuIlmz/jSzf9jezL2sftUxub0NY18yTKQXEtd+Efn749Ns=" /></div><div class="header-container"><nav class="top-bar" data-topbar=""><ul class="title-area"><li class="name"><h1><a href="/"><img alt="Logo" src="../img/logo.png" /></a></h1></li><li class="toggle-topbar menu-icon"><a href="#"><span>Menu</span></a></li></ul><section class="top-bar-section"><!-- Right Nav Section --><ul class="right"><li><a href="/">Home</a></li><li class="search-toggle"><a href="#">Search</a></li><li><a href="../About.aspx">About</a></li><li><a href="../Contact.aspx">Contact</a></li><li class="controller"><img alt="Controller logo" class="controller-logo" src="../img/controller-logo.png" /></li></ul></section></nav><section class="search-menu"><div class="row"><div class="large-4 columns"><div class="button"><a href="../SearchContracts.aspx">City Contracts</a></div></div><div class="large-4 columns"><div class="button"><a href="../SearchContributions.aspx">Campaign Finance</a></div></div><div class="large-4 columns"><div class="button"><a href="../SearchLobbyists.aspx">Lobbyists</a></div></div></div></section></div><div class="main-container">    <span id="FlashErrorMessage"></span>        <div class="gridview">    <div class="search-page">        <div class="row controls">            <div class="medium-4 large-6 columns campaign-nav">                <nav>                    <ul>                        <li><a href="#">City Contracts</a></li>                    </ul>                </nav>            </div>            <div class="medium-8 large-6 columns">                <div class="pagination right">                    <span id="ContentPlaceHolder1_lblPageSize">View:</span>                    <select name="ctl00$ContentPlaceHolder1$ddlPageSize" onchange="javascript:setTimeout('__doPostBack(\'ctl00$ContentPlaceHolder1$ddlPageSize\',\'\')', 0)" id="ContentPlaceHolder1_ddlPageSize">        <option selected="selected" value="10">10 per page</option>        <option value="25">25 per page</option>        <option value="50">50 per page</option>        <option value="100">100 per page</option></select>                    <span id="ContentPlaceHolder1_lblCurrentPage" class="results">Results: 21 - 22 of 22</span>                </div>            </div>        </div>        <div class="row search-row">            <div class="medium-4 large-3 columns">                <div class="search-field">                    <h2>Department</h2>                    <select name="ctl00$ContentPlaceHolder1$CityDepartment" id="ContentPlaceHolder1_CityDepartment">        <option selected="selected" value="0">All Organizations</option>        <option value="600000">Bureau of Neighborhood Empowerment</option>        <option value="101200">City Clerk</option>        <option value="101100">City Council</option>        <option value="110000">City Planning</option>        <option value="999900">Civilian Review Board</option>        <option value="106000">Controller's Office</option>        <option value="104000">Dept. of Mobility &amp; Infrastructure</option>        <option value="102300">Equal Opportunity Review Commission</option>        <option value="840000">Equipment Leasing Authority</option>        <option value="107000">Finance</option>        <option value="121000">GS-Bureau of Administration</option>        <option value="105000">Human Relations Comm.</option>        <option value="109000">Human Resources</option>        <option value="103000">Innovation &amp; Performance</option>        <option value="108000">Law</option>        <option value="102000">Mayor's Office</option>        <option value="999200">Nondepartmental - Citywide</option>        <option value="999100">Nondepartmental - Debt Service</option>        <option value="999400">Nondepartmental - Miscellaneous</option>        <option value="999300">Nondepartmental - Personnel Rela</option>        <option value="600300">Office of Management and Budget</option>        <option value="600500">Office of Municipal Investigations</option>        <option value="500000">Parks and Recreation</option>        <option value="270000">Permits, Licenses and Inspections</option>        <option value="106500">Procurement</option>        <option value="210000">PS-Admn and Support Srvc Bur</option>        <option value="213000">PS-Disaster Assistance</option>        <option value="220000">PS-Emergency Med Services Bur</option>        <option value="250000">PS-Fire Bureau</option>        <option value="230000">PS-Police Bureau</option>        <option value="400000">Public Works</option>        <option value="820000">Urban Redevelopment Authority</option></select>                </div>                <div class="search-field">                    <h2>Contract Type</h2>                    <select name="ctl00$ContentPlaceHolder1$ContractType" id="ContentPlaceHolder1_ContractType">        <option selected="selected" value="0">All Services</option>        <option value="68">COMMODITY</option>        <option value="69">COOP AGREEMENT</option>        <option value="70">COUNTY</option>        <option value="71">DEPOSITORY</option>        <option value="72">EASEMENT</option>        <option value="74">EQUIPMENT</option>        <option value="76">GRANT AGREEMENT</option>        <option value="77">LEASE AGREEMENT</option>        <option value="84">LICENSE AGREEMENT</option>        <option value="78">MAINTENANCE</option>        <option value="79">PROFESSIONAL SERVICES</option>        <option value="80">REIMBURSEMENT</option>        <option value="81">SALE AGREEMENT</option>        <option value="82">SERVICE</option>        <option value="83">STATE</option></select>                </div>                <div class="search-field">                    <h2>Vendor Name</h2>                    <table id="ContentPlaceHolder1_rbVendor" hidden="true">        <tbody><tr>                <td><input id="ContentPlaceHolder1_rbVendor_0" type="radio" name="ctl00$ContentPlaceHolder1$rbVendor" value="B" /><label for="ContentPlaceHolder1_rbVendor_0">Begins with</label></td>        </tr><tr>                <td><input id="ContentPlaceHolder1_rbVendor_1" type="radio" name="ctl00$ContentPlaceHolder1$rbVendor" value="C" checked="checked" /><label for="ContentPlaceHolder1_rbVendor_1">Contains</label></td>        </tr><tr>                <td><input id="ContentPlaceHolder1_rbVendor_2" type="radio" name="ctl00$ContentPlaceHolder1$rbVendor" value="E" /><label for="ContentPlaceHolder1_rbVendor_2">Exact</label></td>        </tr></tbody></table>                    <input name="ctl00$ContentPlaceHolder1$Vendor" type="text" id="ContentPlaceHolder1_Vendor" placeholder="Name of Vendor... " />                </div>                <div class="search-field">                    <h2>Keyword</h2>                    <input name="ctl00$ContentPlaceHolder1$Keywords" type="text" id="ContentPlaceHolder1_Keywords" placeholder="Keyword..." />                </div>                <div class="search-field">                    <h2>Contract Number</h2>                    <input name="ctl00$ContentPlaceHolder1$ContractID" type="text" id="ContentPlaceHolder1_ContractID" placeholder="Contract Number..." />                </div>                <div class="search-field">                    <h2>Contract Approval Date</h2>                    <div class="row date-select">                        <div class="large-12 columns">                            <label class="date">From:</label>                            <input placeholder="Start" type="date" id="dtmStart" name="dtmStart" value="2018-09-25" />                        </div>                        <div class="large-12 columns">                            <label class="date">To:</label>                            <input placeholder="End" type="date" id="dtmFinish" name="dtmFinish" value="2018-10-09" />                        </div>                    </div>                </div>                <div class="search-field">                    <h2>Search by Amount</h2>                    <table id="ContentPlaceHolder1_ContractAmountType">        <tbody><tr>                <td><input id="ContentPlaceHolder1_ContractAmountType_0" type="radio" name="ctl00$ContentPlaceHolder1$ContractAmountType" value="Contract" checked="checked" /><label for="ContentPlaceHolder1_ContractAmountType_0">Contract</label></td><td><input id="ContentPlaceHolder1_ContractAmountType_1" type="radio" name="ctl00$ContentPlaceHolder1$ContractAmountType" value="Paid" /><label for="ContentPlaceHolder1_ContractAmountType_1">Paid</label></td>        </tr></tbody></table>                    <div class="range-slider">                        <label>Minimum Amount</label>                        <input class="input-range" max="10000" min="0" type="range" value="0" id="dblMinContract" name="dblMinContract" />                        <span id="minContract" class="range-value">0</span>                    </div>                    <div class="range-slider">                        <input type="hidden" id="MaxContractField" value="120000000" />                        <input type="hidden" id="StickyMinContract" value="0" />                        <input type="hidden" id="StickyMaxContract" value="120000000" />                        <label>Maximum Amount</label>                        <input class="input-range" min="10001" type="range" id="dblMaxContract" name="dblMaxContract" max="120000000" />                        <span id="maxContract" class="range-value">120,000,000</span>                    </div>                </div>                <div class="search-field">                    <input type="submit" name="ctl00$ContentPlaceHolder1$ImageButton1" value="Search" id="ContentPlaceHolder1_ImageButton1" class="button" />                </div>            </div>            <div class="medium-8 large-9 columns">                <div class="search-field">                    <h2>Sort Results by:</h2>                    <select name="ctl00$ContentPlaceHolder1$ddlSortContracts" onchange="javascript:setTimeout('__doPostBack(\'ctl00$ContentPlaceHolder1$ddlSortContracts\',\'\')', 0)" id="ContentPlaceHolder1_ddlSortContracts" class="sort-dropdown">        <option selected="selected" value="amount">Contract Amount</option>        <option value="DepartmentID">Department</option>        <option value="Service">Contract Type</option>        <option value="VendorName">Vendor Name</option>        <option value="DateCountersigned">Approval Date</option></select>                    <input type="image" name="ctl00$ContentPlaceHolder1$imgSortDirection" id="ContentPlaceHolder1_imgSortDirection" src="img/downarrow.gif" />                </div>                <div class="items-container">                            <div class="item">                                <h2><a href="VendorDetail.aspx?ID=0000229973">HOUSING AUTHORITY OF THE CITY</a></h2>                                <div class="price-group">                                    <span class="original">Currrent Contract Amount: $0.00</span>                                    <span class="current"> Original Contract Amount</span>                                </div>                                <div class="price-group">                                    <span class="current">Amount Paid: $0</span>                                </div>                                <div class="label-group">                                    <div class="label-item">                                        <div class="type">Type</div>                                        <div class="title">REIMBURSEMENT</div>                                    </div>                                    <div class="label-item">                                        <div class="type">Department</div>                                        <div class="title">PS-Police Bureau</div>                                    </div>                                </div>                                <div class="agenda">                                    <span class="title">Contract                                                             <i><b><a href="ContractDetail.aspx?ID=52614&amp;sup=0">                                                 52614                                             </a></b></i>                                        Term:</span>                                    <span>08/30/2018 —09/14/2020</span>                                </div>                                <div class="description">                                    <p>INCOME MEMO/SUPPLEMENTAL POLICE SERVICES FOR AFFORDABLE HOUSING COMMUNITIES</p>                                </div>                                <span class="current">                                    <div id="ContentPlaceHolder1_rptContracts_pnlContractPDF_0" class="PDFPanel">                                        <label>Contract</label>                                        <input type="image" name="ctl00$ContentPlaceHolder1$rptContracts$ctl00$ibtnContractPDF" id="ContentPlaceHolder1_rptContracts_ibtnContractPDF_0" src="img/pdficon.gif" /></div>                                </span>                            </div>                            <div class="item">                                <h2><a href="VendorDetail.aspx?ID=0000399710">SOMETHING INDUSTRIES/SOMETHING FIREGROUND SOLUTIONS  </a></h2>                                <div class="price-group">                                    <span class="original">Currrent Contract Amount: $0.00</span>                                    <span class="current"> Original Contract Amount</span>                                </div>                                <div class="price-group">                                    <span class="current">Amount Paid: $0</span>                                </div>                                <div class="label-group">                                    <div class="label-item">                                        <div class="type">Type</div>                                        <div class="title">COMMODITY</div>                                    </div>                                    <div class="label-item">                                        <div class="type">Department</div>                                        <div class="title">PS-Fire Bureau</div>                                    </div>                                </div>                                <div class="agenda">                                    <span class="title">Contract                                                             <i><b><a href="ContractDetail.aspx?ID=52616&amp;sup=0">                                                 52616                                             </a></b></i>                                        Term:</span>                                    <span>08/29/2018 —08/31/2021</span>                                </div>                                <div class="description">                                    <p>MEMO SOLE SOURCE PROVIDER/3612 ONE-PIECE HIGH RISE NOZZLE SYSTEM</p>                                </div>                                <span class="current">                                    <div id="ContentPlaceHolder1_rptContracts_pnlContractPDF_1" class="PDFPanel">                                        <label>Contract</label>                                        <input type="image" name="ctl00$ContentPlaceHolder1$rptContracts$ctl01$ibtnContractPDF" id="ContentPlaceHolder1_rptContracts_ibtnContractPDF_1" src="img/pdficon.gif" /></div>                                </span>                            </div>                </div>                <div class="bottomnav">                    <div class="bottomnavbtns">                        <div class="large-12 columns pagination-controls">                            <div class="large-3 columns prev button">                                <input type="submit" name="ctl00$ContentPlaceHolder1$ibtnFirstPageTop" value="First" id="ContentPlaceHolder1_ibtnFirstPageTop" class="button prev" />                            </div>                            <div class="large-3 columns prev button">                                <input type="submit" name="ctl00$ContentPlaceHolder1$ibtnPrevPageTop" value="Previous" id="ContentPlaceHolder1_ibtnPrevPageTop" class="button prev" />                            </div>                            <div class="large-3 columns prev button">                                <input type="submit" name="ctl00$ContentPlaceHolder1$ibtnNextPageTop" value="Next" id="ContentPlaceHolder1_ibtnNextPageTop" disabled="disabled" class="aspNetDisabled" />                            </div>                            <div class="large-3 columns prev button">                                <input type="submit" name="ctl00$ContentPlaceHolder1$ibtnLastPageTop" value="Last" id="ContentPlaceHolder1_ibtnLastPageTop" disabled="disabled" class="aspNetDisabled" />                            </div>                        </div>                    </div>                </div>            </div>        </div>    </div>        </div>            <div class="row">            <div class="large-12 columns">                <div class="fb-share-button fb_iframe_widget" style="float:right" data-layout="button" data-size="large" data-mobile-iframe="true" fb-xfbml-state="rendered" fb-iframe-plugin-query="app_id=274942492605472&amp;container_width=43&amp;href=http%3A%2F%2Fwww.redacted.fake%2FSearchContracts.aspx%3FstartDateRange%3D2018-09-25%26endDateRange%3D2018-10-09%26amtMax%3D120000000%26click%3D1&amp;layout=button&amp;locale=en_US&amp;mobile_iframe=true&amp;sdk=joey&amp;size=large"><span style="vertical-align: bottom; width: 73px; height: 28px;"></span></div>                            </div>            </div>    <footer class="row"><div class="large-8 columns">    <ul>        <li>            <a href="http://redacted.fake/controller/controller.html" target="_blank">Office of the City Controller →</a>        </li>    </ul></div><div class="large-4 columns">    <ul class="footer-links">        <li>            <a id="SearchTips" class="button expand" href="SearchTips.aspx">Search Tips<i class="fa fa-search"></i></a></li>        <li>            <a id="HyperLink10" class="button expand" href="ReportFraud.aspx">Report Fraud<i class="fa fa-bolt"></i></a></li>        <li>            <a id="Contact" class="button expand" href="Contact.aspx">Contact Us<i class="fa fa-send"></i></a></li>    </ul></div></footer>    </div><div class="copyright"><div class="row"><div class="large-12 columns"><span><img alt="Footer logo" src="../img/footer-logo.png" /></span><span class="copy">    Copyright 2018</span></div></div></div>                    </form></body></html>`;

const selectedClass = "-autoscrape-selected";
const selectedParentClass = "-autoscrape-selected-parent";
// NOTE: if overClass changes, change the regex replacement
// on the HTML chunk below (bottom of runUI method)
const overClass = "-autoscrape-over";
// save our LCA HTML chunk here (HACK)
let LCA = null;

/**
 * Get the absolute depth of a element, from its target
 * property. This doesn't differentiate between equal depth
 * nodes from different branches.
 */
const getDepth = (target) => {
  let parent = target.parentNode;
  let depth = 0;
  while (parent !== null) {
    depth++;
    parent = parent.parentNode;
  }
  return depth;
};

/**
 * Get the lowest common ancestor (LCA), as an Element, of a
 * set of element nodes. Note that this is *not* an optimal
 * LCA algorithm.
 */
const getLCA = (nodes) => {
  const depthNodes = {};
  let lowest = null;

  if (nodes.length === 1) {
    return nodes[0].target.parentNode;
  }

  // get the depth of each node
  for (const nodeIx in nodes) {
    const node = nodes[nodeIx];
    const depth = getDepth(node.target);
    if (depthNodes[depth] === undefined) {
      depthNodes[depth] = [];
    }
    depthNodes[depth].push(node);
    if (lowest === null || lowest > depth) {
      lowest = depth;
    }
  }

  // find the parent node of each depth node and
  // loop until every node has a parent node of
  // the same height
  let eqDepthParents = [];
  for (const depth in depthNodes) {
    for (const nIx in depthNodes[depth]) {
      let parentNode = depthNodes[depth][nIx].target.parentNode;
      if (depth == lowest) {
        eqDepthParents.push(parentNode);
      }
      else {
        let i = depth;
        for (; i > lowest; i--) {
          parentNode = parentNode.parentNode;
        }
        eqDepthParents.push(parentNode);
      }
    }
  }

  // now that all the nodes have a parent of the same height,
  // check to see if the common-height parent is the
  // same parent for all, if yes, return it
  // if it's not, go up another level and see if those
  // are all the same, continue until this it true
  let pDepth = lowest;
  while (pDepth > 0) {
    const allEqual = eqDepthParents.every((v, i, a) => {
      return v === a[0];
    });
    if (allEqual) {
      return eqDepthParents[0];
    }
    pDepth--;
    const nextParents = [];
    for (nIx in eqDepthParents) {
      const node = eqDepthParents[nIx];
      nextParents.push(node.parentNode);
    }
    eqDepthParents = nextParents;
  }

  // we found no solution!
  return null;
};

/**
 * Set up the mouse over and clicking functionality
 * along with the highlighting of the LCA.
 */
const runUI = () => {
  // clear the chunk display
  $("#lca-html").text("").html();
  $("#hext-template").text("").html();

  // grab all HTML document's elements
  const els = $("#main").find("*");
  let selectedEls = [];
  let parentNode = null;

  // we need both enter/leave and over/out pairs
  // for this to work correctly with nested nodes
  els.on("mouseenter mouseover", (e) => {
    e.stopPropagation();
    $(e.target).addClass(overClass);
  });
  els.on("mouseleave mouseout", (e) => {
    e.stopPropagation();
    $(e.target).removeClass(overClass);
  });

  // when we click, add the node to our node list
  // and also outline it
  els.on("click", (e) => {
    // don't propogate click upwards
    e.preventDefault()
    e.stopPropagation();

    // add to selected
    const selIx = selectedEls.indexOf(e);
    if(selIx === -1) {
      $(e.target).addClass(selectedClass);
      selectedEls.push(e);
    }
    // remove from selected
    else {
      $(e.target).removeClass(selectedClass);
      selectedEls.splice(selIx, 1);
    }

    // highlight parent element if we have some nodes
    const lca = getLCA(selectedEls);
    $("*").removeClass(selectedParentClass);
    $(lca).addClass(selectedParentClass);

    // this really shouldn't happen anymore. but we have
    // to recover from the possibility somehow
    if (!lca) {
      $("*").removeClass(selectedParentClass);
      $("*").removeClass(selectedClass);
      selectedEls = [];
    }
    // we have an LCA, grab the outerHTML and display the chunk
    else {
      // NOTE: if overClass changes, this needs to change
      const chunk = lca.outerHTML.replace(/\s*-autoscrape-over\s*/, "");
      $("#lca-html").text(chunk).html();
      LCA = chunk;
    }
  });
};

/**
 * Cancel all handlers and freeze the HTML chunk.
 */
const stopUI = () => {
  const els = $("#main").find("*");
  els.removeClass(overClass);
  els.off();
  els.on("click", (e) => {
    e.preventDefault()
    e.stopPropagation();
  });
  $("#complete").hide();
};

/**
 * Convert an HTML chunk, with selected classes attached, into
 * a hext template where the selected nodes are extracted.
 */
const html2hext = (html) => {
  const parsed = $.parseHTML(html);
  if (parsed.length !== 1) {
    console.error("Cannot build a Hext template without a single root node");
    return;
  }
  const root = parsed[0];

  let output = "";

  /**
   * Recursive plan:
   * 1) check if element has selected class
   *   a) yes: build a @text:COL[N], href if a, src if img
   * 2) remove all attributes from element
   * 3) check for children nodes
   *   a) yes:
   *     i) write opening tag w/ optional extractor
   *     ii) recurse into children node in a loop
   *     iii) write closing tag
   *   b) no: write full tag w/ optional extractor
   */
  let colN = 1;
  const transform = (node) => {
    if (!node) {
      return;
    }

    // build selector
    let selectors = [];
    if (node.classList.contains(selectedClass)) {
      selectors.push(`@text:COLUMN-${colN++}`);
      switch (node.tagName) {
        case "IMG":
          if (node.getAttribute("src")) {
            selectors.push(`src:COLUMN-${colN++}`);
          }
          break;
        case "A":
          if (node.getAttribute("href")) {
            selectors.push(`href:COLUMN-${colN++}`);
          }
          break;
        default:
          break;
      }
    }

    const selectorStr = selectors.join(" ");

    // remove attributes
    for (let i in node.attributes) {
      if (node.hasOwnProperty(i)) {
        const name = node.attributes[i].name;
        node.removeAttribute(name);
      }
    }


    let children = node.children;
    if (children.length === 0) {
      // write opening & closing tag w/ selectors
      output += `<${node.tagName} ${selectorStr} />`;
    }
    else {
      // write opening tag w/ selectors
      output += `<${node.tagName} ${selectorStr}>`;
      for (const i in children) {
        if (children.hasOwnProperty(i)) {
          const child = children[i];
          transform(child, output);
        }
      }
      // write closing tag
      output += `</${node.tagName}>`;
    }

  };

  transform(root);
  return output;
};

// Set up our different HTML document examples
const btnMap = [{
  tag: "#loader1",
  html: html1
}, {
  tag: "#loader2",
  html: html2
}];

/**
 * TODO: remove iframe, link, style, script
 * TODO: remove all event listeners before adding any
 * of our own here.
 * TODO: go through all links and remove/replace the href?
 * this will mess with the DOM though and would break the
 * Hext template.
 *
 * I have done this manually in the HTML document, but we
 * need to think about potential security problems here
 * w.r.t. loading arbitarty HTML and rendering it.
 */
$(document).on("ready", () => {
  $("#complete").hide();
  btnMap.forEach((obj) => {
    $(obj.tag).on("click", () => {
      $("#main").html("");
      $("#main").html(obj.html);
      $("#complete").show();
      runUI();
    });
  });
  $("#complete").on("click", () => {
    $("#complete").hide();
    stopUI();
    const hext = html2hext(LCA.replace("\n", "").trim());
    $("#hext-template").text(hext).html();
  });
});

