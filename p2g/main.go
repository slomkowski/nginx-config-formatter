package main

import (
	"bufio"
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"regexp"
	"strings"

	iconv "github.com/djimenez/iconv-go"
	"github.com/urfave/cli"
	"github.com/wxnacy/wgo/arrays"
)

// ConExchange 内容交换
type ConExchange struct {
	// EntireConf 整个内容
	EntireConf string
	// Lines 所有按行的内容
	Lines []string
	// CurrentLines 当前拼接行的内容
	CurrentLines []string
	// LastQmark 引号标志 "  '
	LastQmark rune

	// QmarkFlag 是否在引号内
	QmarkFlag bool
	// LastRune 上一个字符
	LastRune rune
}

// TemplateVariableOpeningTag 替换${}里的  {
var TemplateVariableOpeningTag string = "___TEMPLATE_VARIABLE_OPENING_TAG___"

// TemplateVariableClosingTag 替换${}里的  }
var TemplateVariableClosingTag string = "___TEMPLATE_VARIABLE_CLOSING_TAG___"

// TemplateRegOpeningTag 替换正文里的 {
var TemplateRegOpeningTag string = "___TEMPLATE_REG_OPENING_TAG___"

// TemplateRegClosingTag 替换正文里的 }
var TemplateRegClosingTag string = "___TEMPLATE_REG_CLOSING_TAG___"

func main() {

	app := cli.NewApp()
	app.EnableBashCompletion = true
	app.Name = "doit-ngxformatter"
	app.Usage = "Nginx配置文件格式化工具"
	app.Author = "yongfu"
	app.Description = "Nginx配置文件格式化工具"
	app.UsageText = "./doit-ngxformatter [-b 2]"

	app.Flags = []cli.Flag{

		cli.StringFlag{
			Name:     "charset, c",
			Value:    "utf-8",
			Required: false,
			Usage:    "当前支持字符集: gbk, gb18030, windows-1252, utf-8",
		},
		cli.IntFlag{
			Name:  "space, s",
			Value: 2,
			Usage: "缩进的空格数, 默认缩进2个空格",
		},
		cli.BoolFlag{
			Name:     "backup, b",
			Required: false,
			Usage:    "是否备份, 默认不备份",
		},
		cli.BoolFlag{
			Name:     "verbose, v",
			Required: false,
			Usage:    "是否显示详细信息, 默认不显示详细信息",
		},
	}

	app.Action = func(c *cli.Context) error {
		blankSpace := c.Int("space")
		backup := c.Bool("backup")
		verbose := c.Bool("verbose")
		charset := c.String("charset")

		fmt.Printf("blankSpace: %v\n", blankSpace)
		fmt.Printf("backup: %v\n", backup)
		fmt.Printf("verbose: %v\n", verbose)
		fmt.Printf("charset: %v\n", charset)

		// 检查字符集
		if !checkCharset(charset) {
			fmt.Printf("不支持的字符集!\n 终止配置文件的格式化!\n")
			return nil
		}

		if c.NArg() > 0 {
			for _, conf := range c.Args() {
				// 防止传入的文件不存在
				if IsFile(conf) {
					// 进行格式化处理
					formatConfigFile(conf, charset, backup, verbose)
				} else {
					fmt.Printf("文件不存在: %v\n", conf)
				}
			}
		} else {
			fmt.Printf("没有传对应的参数\n")
		}
		return nil
	}
	app.Run(os.Args)
}

// checkCharset 检查是否为受支持的字符集
func checkCharset(s string) bool {
	charsetList := []string{"gbk", "gb18030", "windows-1252", "utf-8"}
	i := arrays.ContainsString(charsetList, s)
	if i == -1 {
		return false
	}
	return true
}

// Exists 判断所给路径文件/文件夹是否存在
func Exists(path string) bool {
	_, err := os.Stat(path) //os.Stat获取文件信息
	if err != nil {
		if os.IsExist(err) {
			return true
		}
		return false
	}
	return true
}

// IsDir 判断所给路径是否为文件夹
func IsDir(path string) bool {
	s, err := os.Stat(path)
	if err != nil {
		return false
	}
	return s.IsDir()
}

// IsFile 判断所给路径是否为文件
func IsFile(path string) bool {
	s, err := os.Stat(path)
	if err != nil {
		return false
	}
	return !s.IsDir()
}

func (d *ConExchange) processLine() {
	for _, k := range d.Lines {
		// 去掉收尾的空格和tab键
		s1 := strings.Trim(k, " ")
		s2 := strings.Trim(s1, "	")

		// 如果以"#"开头, 则直接追加到行内
		if strings.HasPrefix(s2, "#") {
			d.CurrentLines = append(d.CurrentLines, s2)
			// 如果是空行
		} else if s2 == "" {
			d.CurrentLines = append(d.CurrentLines, s2)
			// 对一行进行处理
		} else {
			s2 = d.applyBracketVariableTags(s2)
			//s2 = d.applyBracketRegTags(s2)
		}
	}

}

// applyBracketVariableTags 替换变量的 { } 为替换字符
func (d *ConExchange) applyBracketVariableTags(line string) string {
	re1, _ := regexp.Compile(`\${\s*(\w+)\s*}`)
	sub := re1.FindSubmatch([]byte(line))

	f := func(s string) string {
		return "$" + TemplateVariableOpeningTag + string(sub[1]) + TemplateVariableClosingTag
	}

	s := re1.ReplaceAllStringFunc(line, f)

	return s
}

// ReadLine 按行读取
func ReadLine(filePth string, hookfn func(string)) error {
	f, err := os.Open(filePth)
	if err != nil {
		return err
	}
	defer f.Close()

	bfRd := bufio.NewReader(f)
	for {
		line, err := bfRd.ReadBytes('\n')
		if err != nil { //遇到任何错误立即返回，并忽略 EOF 错误信息
			if err == io.EOF {
				hookfn(string(line))
				return nil
			}
			return err
		}
		hookfn(string(line))
	}
	return nil
}

// ReadAll 读取到file中，再利用ioutil将file直接读取到[]byte中, 这是最优
func ReadAll(filePth string) string {
	f, err := os.Open(filePth)
	if err != nil {
		fmt.Println("read file fail", err)
		return ""
	}
	defer f.Close()

	fd, err := ioutil.ReadAll(f)
	if err != nil {
		fmt.Println("read to fd fail", err)
		return ""
	}

	return string(fd)
}

// ToLines 变成按行的数据
func ToLines(contents string) []string {
	f := func(c rune) bool {
		if c == '\n' {
			return true
		}
		return false
	}
	return strings.FieldsFunc(contents, f)
}

func (d *ConExchange) applyBracketTemplateTags(contents string) {
	var b []rune
	b = []rune(contents)
	for _, k := range b {
		// 判断当前字符为引号,并且是非转义的引号
		if (k == '"' || k == '\'') && d.LastRune != '\\' {
			// 判断该引号是否和前面的引号配对或为第一个引号.
			// if d.LastQmark ==  || d.LastQmark == k {
			// 	d.QmarkFlag = reverse_in_quotes_status(d.QmarkFlag)
			// }

			// 配对完成后,需要将 Qmark 置为nil, 同时把QmarkFlag标记为False

			fmt.Printf("%#v", d.QmarkFlag)
			fmt.Printf("k: 是引号: %c\n", k)
		} else {
			fmt.Printf("k: %c, %T\n", k, k)
		}

	}
}

func reverseInQuotesStatus(status bool) bool {
	if status == true {
		return false
	}

	return true
}

func formatConfigFile(configFilePath string, charset string, backup bool, verbose bool) {
	/*
		1. 首先以正确的编码打开文件
		2. 然后以正确的编码读取文件
		3. 判断文件内容是否为空
		4. 判断是否需要备份, 若要备份, 则进行备份(以原有的编码进行备份).
			4.1 判断是否需要显示详细信息
		5. 以utf8格式转码, 然后进行文件格式化
			5.1 将格式化后的内容, 以原编码格式写入到文件.

	*/

	// 获取文件内容, 并转换为utf-8编码
	fc := ReadAll(configFilePath)
	if charset != "utf-8" {
		// 转换为utf8字符集
		fc, _ = iconv.ConvertString(fc, charset, "utf-8")
	}

	// 判断文件是否为空
	if len(fc) == 0 {
		fmt.Printf("%v是一个空文件", configFilePath)
		return
	}

	// 此方法不用关心原来的字符集是什么, 复制的文件还是原来的字符集.
	if backup == true {
		_, err := CopyFile(configFilePath, configFilePath+"~")
		if err != nil {
			fmt.Println(err)
			// 当出现备份错误的时候, 不再进行后面的真正格式化
			return
		}
	}

	// 具体执行配置文件格式化
	fcNew, err := formatConfigContent(fc)
	if err != nil {
		fmt.Println(err)
		// 当格式化出错时, 不再进行 格式化后的文件写入到文件
		return
	}

	// 进行编码格式转换
	if charset != "utf-8" {
		fcNew, _ = iconv.ConvertString(fcNew, "utf-8", charset)
	}

	// 写入新文件
	err = writeNewConfig(configFilePath, fcNew)
	if err != nil {
		fmt.Println(err)
	}
}

func formatConfigContent(fc string) (string, error) {
	return fc, nil
}

func writeNewConfig(Path string, content string) error {
	f, err := os.OpenFile(Path, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	_, err = io.WriteString(f, content) //写入文件(字符串)
	if err != nil {
		return err
	}
	return nil
}

// CopyFile 复制文件
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
