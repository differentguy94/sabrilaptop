#!/bin/bash
# zworks.net — server inventory (READ-ONLY). Run in cPanel > Terminal, then send the output.
# يقرأ فقط ولا يغيّر أي شيء. انسخه كاملاً والصقه في cPanel ← Terminal ثم أرسل الناتج.
set +e
H="$HOME"
echo "=== $(date -u) | user=$(whoami) | home=$H"
echo; echo "=== PHP"; php -v 2>/dev/null | head -1; ls /opt/cpanel/ 2>/dev/null | grep -i ea-php | tr '\n' ' '; echo
echo; echo "=== Disk usage (top-level, GB) — what the 17 GB really is"
du -sh "$H"/* "$H"/.[!.]* 2>/dev/null | sort -rh | head -15
echo; echo "--- public_html breakdown"; du -sh "$H"/public_html/* 2>/dev/null | sort -rh | head -15
echo; echo "--- mail size"; du -sh "$H"/mail 2>/dev/null
echo; echo "--- old backups/archives lying around"; find "$H" -maxdepth 3 \( -name "*.tar.gz" -o -name "*.zip" -o -name "*.wpress" -o -name "backup-*" \) -size +50M -printf "%s\t%p\n" 2>/dev/null | sort -rn | head -10
echo; echo "=== WordPress installs"
for d in "$H/public_html" "$H/public_html/Decor"; do
  echo "--- $d"
  [ -f "$d/wp-includes/version.php" ] && grep -E "^\\\$(wp_version|required_php_version)" "$d/wp-includes/version.php"
  if command -v wp >/dev/null 2>&1; then
    (cd "$d" && wp core version --skip-plugins --skip-themes 2>/dev/null | sed 's/^/core: /'
     wp option get siteurl --skip-plugins --skip-themes 2>/dev/null | sed 's/^/siteurl: /'
     wp option get blog_public --skip-plugins --skip-themes 2>/dev/null | sed 's/^/blog_public(1=indexable): /'
     wp option get WPLANG --skip-plugins --skip-themes 2>/dev/null | sed 's/^/WPLANG: /'
     wp theme list --status=active --skip-plugins --skip-themes 2>/dev/null
     wp plugin list --fields=name,status,version,update --skip-plugins --skip-themes 2>/dev/null
     wp post list --post_type=post --post_status=publish --format=count --skip-plugins --skip-themes 2>/dev/null | sed 's/^/published posts: /'
     wp post list --post_type=product --post_status=publish --format=count --skip-plugins --skip-themes 2>/dev/null | sed 's/^/published products: /'
     wp db size --human-readable --skip-plugins --skip-themes 2>/dev/null | sed 's/^/db size: /'
     wp cron event list --fields=hook,next_run_relative --skip-plugins --skip-themes 2>/dev/null | head -25)
  else
    echo "(wp-cli not found) plugins:"; ls "$d/wp-content/plugins" 2>/dev/null | tr '\n' ' '; echo; echo "theme:"; ls "$d/wp-content/themes" 2>/dev/null | tr '\n' ' '; echo
  fi
  echo "--- .htaccess (first 40 lines)"; head -40 "$d/.htaccess" 2>/dev/null
  echo "--- robots.txt file?"; ls -la "$d/robots.txt" 2>/dev/null || echo "none (virtual)"
done
echo; echo "=== Googlebot in access logs (last 30 days): status code counts"
for f in "$H"/access-logs/* "$H"/logs/*; do
  [ -f "$f" ] || continue
  echo "--- $f"; grep -i "Googlebot" "$f" 2>/dev/null | awk '{print $9}' | sort | uniq -c | sort -rn | head -8
  grep -i "Googlebot" "$f" 2>/dev/null | awk '{print $7}' | sed 's/?.*//' | sort | uniq -c | sort -rn | head -10
done
echo; echo "=== Cron jobs"; crontab -l 2>/dev/null | head -20
echo; echo "=== Done"
