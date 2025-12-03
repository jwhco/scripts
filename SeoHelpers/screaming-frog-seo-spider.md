# Screaming Frog SEO Spider Headless

## Requirement

- Run Screaming Frog SEO Spider from K8S pod headless. Be able to run against a list of websites, without user intervension. Time can focus on looking at report output.


## Installation

```bash
apt update -y
apt install -y wget
wget https://download.screamingfrog.co.uk/products/seo-spider/screamingfrogseospider_23.1_all.deb
apt install ./screamingfrogspider_*_.deb
```

## Running

```base
cd $WORKINGDIR/domain.tld/
screamingfrogseospider --crawl https://www.jwhco.com/ --headless --save-crawl
```

## Use Case

- For old PHP based `iunctura.com` a sitemap can be made on the K8S, saved to a working folder, then uploaded to production.

/EOF/