package main

import (
	"bufio"
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"regexp"
	"strings"

	"github.com/urfave/cli"
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
	app.Name = "doit-ngxformatter"
	app.Usage = "Nginx配置文件格式化工具"
	app.Author = "yongfu"
	app.Description = "Nginx配置文件格式化工具"
	app.UsageText = "./doit-ngxformatter [-b 2]"

	app.Flags = []cli.Flag{
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
	}

	app.Action = func(c *cli.Context) error {
		blankSpace := c.Int("space")
		backup := c.Bool("backup")

		if c.NArg() > 0 {
			for _, k := range c.Args() {
				if IsFile(k) {
					// 每个配置文件, 不同的实例地址
					var d = new(ConExchange)
					d.QmarkFlag = false

					fmt.Printf("== k ==: %v\n", k)
					// ReadLine(k, processLine)
					// 获取配置文件的整个内容
					d.EntireConf = ReadAll(k)
					// 获取配置文件的每行的内容
					d.Lines = ToLines(d.EntireConf)
					d.processLine()
					// 对每一行进行处理
					//    a. 去掉收尾的空格
					//    b. 查找是否在引号内
					//    c. 替换非引号内的 "{" 和 "}"

					// applyBracketTemplateTags(a)
				} else {
					fmt.Printf("文件不存在: %v\n", k)
				}
			}
			fmt.Printf("blankSpace: %v\n", blankSpace)
			fmt.Printf("backup: %v\n", backup)
		} else {
			fmt.Printf("没有传对应的参数")
		}
		return nil
	}
	app.Run(os.Args)
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

func reverse_in_quotes_status(status bool) bool {
	if status == true {
		return false
	}

	return true
}
