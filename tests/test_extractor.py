CASES = [{
    "extractor": """
<article class="lawyer">
  <a>
    <img style:replace(/background: url\((.*)\);/, "\1"):prepend("https://texasbar.com"):profileImg />
  </a>
  <div>
    <h3>
      <a href:prepend("https://texasbar.com"):profileLink >
        <span:nth-child(1) @text:namePrefix />
        <span:nth-child(2) @text:nameFirst />
        <span:nth-child(3) @text:nameLast />
        <span:nth-child(4) @text:nameSuffix/>
      </a>
    </h3>
    <h5 @text:affiliation />
    <p:attribute-count(0) @text:practiceLocation />
    <p class="address" @text:address />
    <p class="areas" @text:practiceArea />
  </div>
</article>""",
    "html": """
<article class="lawyer">
  <div class="no-img">
    <a href="/AM/Template.cfm?Section=Find_A_Lawyer&amp;template=/Customsource/MemberDirectory/MemberDirectoryDetail.cfm&amp;ContactID=282365">
      <!--
        <img src="/AM/templates/layoutcatalog/1601/Images/ProfilePhotoPlaceholder.gif" title="State Bar Seal" alt="State Bar Seal" class="avatar"/>
      -->
      <img style="background: url(/AM/templates/layoutcatalog/1601/Images/ProfilePhotoPlaceholder.gif);" class="avatar">
    </a>
  </div>
  <div class="avatar-column">
    <!-- Determine which status class should be displayed -->
    <h3>
      <span class="status-icon blue triangle"></span>
      <a href="/AM/Template.cfm?Section=Find_A_Lawyer&amp;template=/Customsource/MemberDirectory/MemberDirectoryDetail.cfm&amp;ContactID=282365">
        <span class="honorific-prefix"></span>
        <span class="given-name">John H.</span>
        <span class="family-name">Smither</span>
        <span class="honorific-suffix"></span>
      </a>
    </h3>
    <h5>Vinson &amp; Elkins LLP</h5>
    <p>
    <strong>Primary Practice Location:</strong>
    Houston,&nbsp;TX
    </p>
    <p class="address">
    1001 Fannin St Ste 2801<br> Houston, TX&nbsp;77002
    </p>
    <p class="areas">
    <strong>Practice Areas:</strong>
    None Specified by Attorney
    </p>
    <a href="/AM/Template.cfm?Section=Find_A_Lawyer&amp;template=/Customsource/MemberDirectory/MemberDirectoryDetail.cfm&amp;ContactID=282365" class="read-more">Full profile</a>
    <!--
      <h4 class="wai">Memberships</h4>
      <ul class="memberships">
      </ul>
    -->
  </div>
  <div class="contact">
    <a href="http://h2vx.com/vcf/https://texasbar.com/AM/Template.cfm?Section=Find_A_Lawyer&amp;template=/Customsource/MemberDirectory/vcard.cfm&amp;ContactID=282365">Download vCard <i class="fa fa-download"></i></a>
    <a href="tel:713-758-2466">Tel: 713-758-2466 <i class="fa fa-phone"></i></a>
  </div>
  <div class="badges">
  </div>
</article>
    """,
}, {
    "extractor": """""",
    "html": """""",
}]
