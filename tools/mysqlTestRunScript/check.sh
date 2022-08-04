rm -rf pass fail retry-pass retry-fail retry-fail
touch pass fail retry-pass retry-fail retry-fail

for i in `ls | grep out1`
do
        #cat $i | grep % | tail | sed -n '$p'
        cat out1 | grep 'pass \]' >> pass
        cat out1 | grep '\[ fail \]' >> fail
        cat out1 | grep '\[ retry-pass ]' >> retry-pass
        cat out1 | grep 'retry-fail \]' >> retry-fail
        cat out1 | grep 'skipped \]' >> skipped

done

pass=`cat pass | wc -l` && echo "pass:${pass}"
fail=`cat fail | wc -l` && echo "fail:${fail}"
retry_pass=`cat retry-pass | wc -l` && echo "retry-pass:${retry_pass}"
retry_fail=`cat retry-fail | wc -l` && echo "retry-fail:${retry_fail}"
skipped=`cat skipped | wc -l` && echo "skipped:${skipped}"
ch=`cat $i | grep '%]' | tail | sed -n '$p'`
echo ${i}:${ch}
echo

