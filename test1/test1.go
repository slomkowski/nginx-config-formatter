package main

import (
	"fmt"
	"io"
	"os"

	"golang.org/x/text/encoding/charmap"
)

// CopyFile 文件复制
func CopyFile(dstName, srcName string) (writeen int64, err error) {
	src, err := os.Open(dstName)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer src.Close()

	dst, err := os.OpenFile(srcName, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer dst.Close()

	return io.Copy(dst, src)

}

func main() {
	CopyFile("/Users/yongfu/git/github.com/rickiel/nginx-config-formatter/test1/a.txt", "/Users/yongfu/git/github.com/rickiel/nginx-config-formatter/test1/b.txt")
	fmt.Println("copy done.")

	f, err := os.Open("/Users/yongfu/git/github.com/rickiel/nginx-config-formatter/test1/gb18030.txt.conf")
	if err != nil {
		// handle file open error
	}
	out, err := os.Create("my_utf8.txt")
	if err != nil {
		// handler error
	}

	//r := charmap.Windows1252.NewDecoder().Reader(f)
	r := charmap.Windows1258.NewDecoder().Reader(f)

	io.Copy(out, r)

	out.Close()
	f.Close()
}
