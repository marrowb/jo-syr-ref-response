#!/usr/bin/env python3
"""
IATI 2.03 Documentation Scraper
Converts the entire IATI 2.03 reference documentation into a single markdown document
using r.jina.ai for markdown conversion.
"""

import requests
import time
import re
from urllib.parse import urlparse
from typing import List, Set
import xml.etree.ElementTree as ET


class IATIDocumentationScraper:
    def __init__(self, base_url: str = "https://iatistandard.org", delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay  # Delay between requests to be respectful
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'IATI Documentation Scraper 1.0'
        })

    def extract_203_urls_from_sitemap(self, sitemap_content: str) -> List[str]:
        """Extract all URLs related to IATI 2.03 from the sitemap"""
        urls = []

        # Parse the sitemap XML
        try:
            root = ET.fromstring(sitemap_content)
            # Handle namespace
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            for url_elem in root.findall('.//ns:url', namespace):
                loc_elem = url_elem.find('ns:loc', namespace)
                if loc_elem is not None:
                    url = loc_elem.text
                    # Filter for IATI 2.03 documentation URLs
                    if '/codelists-json/iati-standard/203/' in url:
                        urls.append(url)

        except ET.ParseError as e:
            print(f"Error parsing sitemap XML: {e}")
            # Fallback: use regex to extract URLs
            pattern = r'<loc>(https://iatistandard\.org/codelists-json/iati-standard/203/[^<]+)</loc>'
            urls = re.findall(pattern, sitemap_content)

        return sorted(list(set(urls)))  # Remove duplicates and sort

    def get_sitemap_urls(self) -> List[str]:
        """Get URLs from the provided sitemap content"""
        # Based on the sitemap provided, extract IATI 2.03 URLs
        sitemap_urls = [
            "https://iatistandard.org/en/iati-standard/203/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/example-xml/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/summary-table/",
            "https://iatistandard.org/en/iati-standard/203/codelists/",
            "https://iatistandard.org/en/iati-standard/203/namespaces-extensions/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/example-xml/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/iati-organisation/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/summary-table/",
            "https://iatistandard.org/en/iati-standard/203/reference/",
            "https://iatistandard.org/en/iati-standard/203/rulesets/",
            "https://iatistandard.org/en/iati-standard/203/rulesets/ruleset-spec/",
            "https://iatistandard.org/en/iati-standard/203/rulesets/standard-ruleset/",
            "https://iatistandard.org/en/iati-standard/203/schema/"
        ]

        # Add all codelist URLs
        codelist_urls = [
            "https://iatistandard.org/en/iati-standard/203/codelists/activitydatetype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/activityscope/",
            "https://iatistandard.org/en/iati-standard/203/codelists/activitystatus/",
            "https://iatistandard.org/en/iati-standard/203/codelists/aidtype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/aidtype-category/",
            "https://iatistandard.org/en/iati-standard/203/codelists/aidtypevocabulary/",
            "https://iatistandard.org/en/iati-standard/203/codelists/budgetidentifier/",
            "https://iatistandard.org/en/iati-standard/203/codelists/budgetidentifiersector/",
            "https://iatistandard.org/en/iati-standard/203/codelists/budgetidentifiersector-category/",
            "https://iatistandard.org/en/iati-standard/203/codelists/budgetidentifiervocabulary/",
            "https://iatistandard.org/en/iati-standard/203/codelists/budgetnotprovided/",
            "https://iatistandard.org/en/iati-standard/203/codelists/budgetstatus/",
            "https://iatistandard.org/en/iati-standard/203/codelists/budgettype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/cashandvouchermodalities/",
            "https://iatistandard.org/en/iati-standard/203/codelists/collaborationtype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/conditiontype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/contacttype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/country/",
            "https://iatistandard.org/en/iati-standard/203/codelists/crsaddotherflags/",
            "https://iatistandard.org/en/iati-standard/203/codelists/crschannelcode/",
            "https://iatistandard.org/en/iati-standard/203/codelists/currency/",
            "https://iatistandard.org/en/iati-standard/203/codelists/descriptiontype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/disbursementchannel/",
            "https://iatistandard.org/en/iati-standard/203/codelists/documentcategory/",
            "https://iatistandard.org/en/iati-standard/203/codelists/documentcategory-category/",
            "https://iatistandard.org/en/iati-standard/203/codelists/earmarkingcategory/",
            "https://iatistandard.org/en/iati-standard/203/codelists/fileformat/",
            "https://iatistandard.org/en/iati-standard/203/codelists/financetype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/financetype-category/",
            "https://iatistandard.org/en/iati-standard/203/codelists/flowtype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/gazetteeragency/",
            "https://iatistandard.org/en/iati-standard/203/codelists/geographicalprecision/",
            "https://iatistandard.org/en/iati-standard/203/codelists/geographicexactness/",
            "https://iatistandard.org/en/iati-standard/203/codelists/geographiclocationclass/",
            "https://iatistandard.org/en/iati-standard/203/codelists/geographiclocationreach/",
            "https://iatistandard.org/en/iati-standard/203/codelists/geographicvocabulary/",
            "https://iatistandard.org/en/iati-standard/203/codelists/humanitarianscopetype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/humanitarianscopevocabulary/",
            "https://iatistandard.org/en/iati-standard/203/codelists/iatiorganisationidentifier/",
            "https://iatistandard.org/en/iati-standard/203/codelists/indicatormeasure/",
            "https://iatistandard.org/en/iati-standard/203/codelists/indicatorvocabulary/",
            "https://iatistandard.org/en/iati-standard/203/codelists/language/",
            "https://iatistandard.org/en/iati-standard/203/codelists/loanrepaymentperiod/",
            "https://iatistandard.org/en/iati-standard/203/codelists/loanrepaymenttype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/locationtype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/locationtype-category/",
            "https://iatistandard.org/en/iati-standard/203/codelists/organisationidentifier/",
            "https://iatistandard.org/en/iati-standard/203/codelists/organisationregistrationagency/",
            "https://iatistandard.org/en/iati-standard/203/codelists/organisationrole/",
            "https://iatistandard.org/en/iati-standard/203/codelists/organisationtype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/otheridentifiertype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/policymarker/",
            "https://iatistandard.org/en/iati-standard/203/codelists/policymarkervocabulary/",
            "https://iatistandard.org/en/iati-standard/203/codelists/policysignificance/",
            "https://iatistandard.org/en/iati-standard/203/codelists/publishertype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/region/",
            "https://iatistandard.org/en/iati-standard/203/codelists/regionvocabulary/",
            "https://iatistandard.org/en/iati-standard/203/codelists/relatedactivitytype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/resulttype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/resultvocabulary/",
            "https://iatistandard.org/en/iati-standard/203/codelists/sector/",
            "https://iatistandard.org/en/iati-standard/203/codelists/sectorcategory/",
            "https://iatistandard.org/en/iati-standard/203/codelists/sectorvocabulary/",
            "https://iatistandard.org/en/iati-standard/203/codelists/tagvocabulary/",
            "https://iatistandard.org/en/iati-standard/203/codelists/tiedstatus/",
            "https://iatistandard.org/en/iati-standard/203/codelists/transactiontype/",
            "https://iatistandard.org/en/iati-standard/203/codelists/unsdg-goals/",
            "https://iatistandard.org/en/iati-standard/203/codelists/unsdg-targets/",
            "https://iatistandard.org/en/iati-standard/203/codelists/verificationstatus/",
            "https://iatistandard.org/en/iati-standard/203/codelists/version/",
            "https://iatistandard.org/en/iati-standard/203/codelists/vocabulary/"
        ]

        # Add detailed activity standard URLs (sampling from sitemap)
        activity_detail_urls = [
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/activity-date/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/activity-scope/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/activity-status/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/budget/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/collaboration-type/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/conditions/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/contact-info/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/description/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/document-link/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/humanitarian-scope/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/iati-identifier/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/location/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/participating-org/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/policy-marker/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/recipient-country/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/recipient-region/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/reporting-org/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/result/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/sector/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/title/",
            "https://iatistandard.org/en/iati-standard/203/activity-standard/iati-activities/iati-activity/transaction/"
        ]

        # Add organization standard URLs
        org_standard_urls = [
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/iati-organisation/document-link/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/iati-organisation/name/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/iati-organisation/organisation-identifier/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/iati-organisation/recipient-country-budget/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/iati-organisation/recipient-org-budget/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/iati-organisation/recipient-region-budget/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/iati-organisation/reporting-org/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/iati-organisation/total-budget/",
            "https://iatistandard.org/en/iati-standard/203/organisation-standard/iati-organisations/iati-organisation/total-expenditure/"
        ]

        return sitemap_urls + codelist_urls + activity_detail_urls + org_standard_urls

    def fetch_markdown_content(self, url: str) -> str:
        """Fetch markdown content using r.jina.ai"""
        jina_url = f"https://r.jina.ai/{url}"

        try:
            print(f"Fetching: {url}")
            response = self.session.get(jina_url, timeout=30)
            response.raise_for_status()

            content = response.text

            # Add URL as header for reference
            markdown_content = f"\n\n---\n# {url}\n\n{content}\n"

            return markdown_content

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return f"\n\n---\n# ERROR: {url}\n\nFailed to fetch content: {e}\n"

    def scrape_all_documentation(self, output_file: str = "iati_203_complete_documentation.md"):
        """Scrape all IATI 2.03 documentation and combine into a single markdown file"""

        urls = self.get_sitemap_urls()
        print(f"Found {len(urls)} URLs to scrape")

        all_content = []

        # Add header
        header = """# IATI 2.03 Complete Documentation

This document contains the complete IATI 2.03 standard documentation scraped and compiled into a single markdown file.

Generated from: https://iatistandard.org/en/iati-standard/203/

---

"""
        all_content.append(header)

        # Process each URL
        for i, url in enumerate(urls, 1):
            print(f"Processing {i}/{len(urls)}: {url}")

            content = self.fetch_markdown_content(url)
            all_content.append(content)

            # Be respectful with delays
            if i < len(urls):  # Don't delay after the last request
                time.sleep(self.delay)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_content))

        print(f"\nScraping complete! Documentation saved to: {output_file}")
        print(f"Total sections processed: {len(urls)}")

        return output_file


def main():
    """Main function to run the scraper"""
    scraper = IATIDocumentationScraper(delay=1.5)  # 1.5 second delay between requests

    try:
        output_file = scraper.scrape_all_documentation()
        print(f"SUCCESS: Complete IATI 2.03 documentation saved to {output_file}")
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()